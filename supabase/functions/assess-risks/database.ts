/** Database operations for storing risk assessments and reasoning traces. */

import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";
import { LLMRiskAssessment, AssessmentResult } from "./types.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

let supabaseClient: SupabaseClient | null = null;

/**
 * Get or create Supabase client.
 */
function getSupabaseClient(): SupabaseClient {
  if (!supabaseClient) {
    if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
    }
    supabaseClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  }
  return supabaseClient;
}

/**
 * Create a reasoning trace in the database.
 */
export async function createReasoningTrace(
  traceData: Record<string, unknown>
): Promise<number> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from("reasoning_traces")
    .insert({
      trace_data: traceData,
    })
    .select("id")
    .single();

  if (error) {
    throw new Error(`Failed to create reasoning trace: ${error.message}`);
  }

  return data.id;
}

/**
 * Create a risk assessment in the database.
 */
export async function createRiskAssessment(
  taskId: number,
  subtaskId: string,
  assessment: LLMRiskAssessment,
  reasoningTraceId?: number
): Promise<number> {
  const supabase = getSupabaseClient();

  // Convert risk factors to JSONB format
  const riskFactors = assessment.risk_factors.map((rf) => ({
    factor: rf.factor,
    description: rf.description,
    severity: rf.severity,
  }));

  const { data, error } = await supabase
    .from("task_risk_assessments")
    .insert({
      task_id: taskId,
      subtask_id: subtaskId,
      risk_level: assessment.risk_level,
      risk_factors: riskFactors,
      mitigation_suggestions: assessment.mitigation_suggestions,
      reasoning_trace_id: reasoningTraceId || null,
    })
    .select("id")
    .single();

  if (error) {
    throw new Error(`Failed to create risk assessment: ${error.message}`);
  }

  return data.id;
}

/**
 * Store multiple risk assessments for a task.
 */
export async function storeAssessments(
  taskId: number,
  results: AssessmentResult[]
): Promise<void> {
  const supabase = getSupabaseClient();

  // Prepare batch insert data
  const assessmentsToInsert = results.map((result) => ({
    task_id: taskId,
    subtask_id: result.subtask_id,
    risk_level: result.assessment.risk_level,
    risk_factors: result.assessment.risk_factors.map((rf) => ({
      factor: rf.factor,
      description: rf.description,
      severity: rf.severity,
    })),
    mitigation_suggestions: result.assessment.mitigation_suggestions,
    reasoning_trace_id: result.reasoning_trace_id || null,
  }));

  const { error } = await supabase
    .from("task_risk_assessments")
    .insert(assessmentsToInsert);

  if (error) {
    throw new Error(`Failed to store assessments: ${error.message}`);
  }
}

/**
 * Verify that a task exists in the database.
 */
export async function verifyTaskExists(taskId: number): Promise<boolean> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from("tasks")
    .select("id")
    .eq("id", taskId)
    .single();

  if (error || !data) {
    return false;
  }

  return true;
}

