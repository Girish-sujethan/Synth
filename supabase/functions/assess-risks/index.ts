/** Supabase Edge Function for risk assessment using Cerebras LLM. */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import {
  RiskAssessmentRequest,
  AssessmentResult,
  LLMRiskAssessment,
} from "./types.ts";
import { assessRisksWithLLM, generateDefaultAssessment } from "./llm-client.ts";
import {
  createReasoningTrace,
  createRiskAssessment,
  verifyTaskExists,
  storeAssessments,
} from "./database.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

/**
 * Main handler for the Edge Function.
 */
serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Parse request body
    const requestData: RiskAssessmentRequest = await req.json();

    // Validate request
    if (!requestData.task_id) {
      return new Response(
        JSON.stringify({ error: "task_id is required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    if (!requestData.subtasks || requestData.subtasks.length === 0) {
      return new Response(
        JSON.stringify({ error: "subtasks array is required and cannot be empty" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Verify task exists
    const taskExists = await verifyTaskExists(requestData.task_id);
    if (!taskExists) {
      return new Response(
        JSON.stringify({ error: `Task ${requestData.task_id} not found` }),
        {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Process each subtask
    const results: AssessmentResult[] = [];
    const dependencies = requestData.dependencies || [];

    for (const subtask of requestData.subtasks) {
      try {
        // Assess risks using LLM
        let assessment: LLMRiskAssessment;
        let reasoningTraceId: number | undefined;

        try {
          assessment = await assessRisksWithLLM(subtask, dependencies);

          // Create reasoning trace
          reasoningTraceId = await createReasoningTrace({
            subtask_id: subtask.id,
            subtask_description: subtask.description,
            assessment: assessment,
            reasoning: assessment.reasoning || "",
            timestamp: new Date().toISOString(),
          });
        } catch (llmError) {
          console.error(
            `LLM assessment failed for subtask ${subtask.id}:`,
            llmError
          );

          // Fallback to default assessment
          assessment = generateDefaultAssessment(subtask);

          // Still create a reasoning trace with error information
          try {
            reasoningTraceId = await createReasoningTrace({
              subtask_id: subtask.id,
              subtask_description: subtask.description,
              error: llmError instanceof Error ? llmError.message : String(llmError),
              fallback_assessment: true,
              timestamp: new Date().toISOString(),
            });
          } catch (traceError) {
            console.error(`Failed to create reasoning trace:`, traceError);
          }
        }

        // Store assessment in database
        try {
          await createRiskAssessment(
            requestData.task_id,
            subtask.id,
            assessment,
            reasoningTraceId
          );

          results.push({
            subtask_id: subtask.id,
            assessment,
            reasoning_trace_id: reasoningTraceId,
          });
        } catch (dbError) {
          console.error(
            `Failed to store assessment for subtask ${subtask.id}:`,
            dbError
          );
          // Continue processing other subtasks even if one fails
        }
      } catch (error) {
        console.error(`Error processing subtask ${subtask.id}:`, error);
        // Continue with next subtask
      }
    }

    // Return success response
    return new Response(
      JSON.stringify({
        success: true,
        task_id: requestData.task_id,
        assessments_created: results.length,
        total_subtasks: requestData.subtasks.length,
        results: results.map((r) => ({
          subtask_id: r.subtask_id,
          risk_level: r.assessment.risk_level,
          risk_factors_count: r.assessment.risk_factors.length,
        })),
      }),
      {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Edge function error:", error);

    return new Response(
      JSON.stringify({
        error: "Internal server error",
        message: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

