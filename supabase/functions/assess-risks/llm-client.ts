/** Cerebras LLM API client for risk assessment analysis. */

import { LLMRiskAssessment, RiskFactor, Subtask, Dependency } from "./types.ts";

const CEREBRAS_API_URL = Deno.env.get("CEREBRAS_API_URL") || 
  "https://api.cerebras.ai/v1/chat/completions";
const CEREBRAS_API_KEY = Deno.env.get("CEREBRAS_API_KEY");
const CEREBRAS_MODEL = Deno.env.get("CEREBRAS_MODEL") || "llama-3.1-8b-instruct";

/**
 * Construct prompt for risk assessment analysis.
 */
function buildRiskAssessmentPrompt(
  subtask: Subtask,
  dependencies: Dependency[] = []
): string {
  const dependencyInfo = dependencies.length > 0
    ? `\nDependencies: ${dependencies.map(d => `${d.id} (${d.type})`).join(", ")}`
    : "";

  return `Analyze the following software development subtask for risk assessment:

Subtask ID: ${subtask.id}
Description: ${subtask.description}${dependencyInfo}

Please assess this subtask for the following risk factors:
1. Legacy system involvement - Does this require working with outdated or legacy systems?
2. Complexity - How complex is the implementation? Consider technical complexity, integration points, and scope.
3. Specialized skills - Does this require rare or specialized technical skills?
4. External dependencies - Are there external systems, APIs, or services that could cause delays or failures?

For each identified risk factor, provide:
- factor: A short identifier (e.g., "legacy_systems", "high_complexity", "specialized_skills", "external_dependencies")
- description: A clear description of the risk
- severity: One of "low", "medium", or "high"

Based on all identified risks, determine an overall risk_level: "low", "medium", or "high".

Also provide mitigation_suggestions: Practical suggestions for reducing or managing the identified risks.

Respond in JSON format with this exact structure:
{
  "risk_level": "low|medium|high",
  "risk_factors": [
    {
      "factor": "string",
      "description": "string",
      "severity": "low|medium|high"
    }
  ],
  "mitigation_suggestions": "string",
  "reasoning": "string (explain your assessment)"
}`;
}

/**
 * Call Cerebras LLM API for risk assessment.
 */
export async function assessRisksWithLLM(
  subtask: Subtask,
  dependencies: Dependency[] = []
): Promise<LLMRiskAssessment> {
  if (!CEREBRAS_API_KEY) {
    throw new Error("CEREBRAS_API_KEY environment variable is not set");
  }

  const prompt = buildRiskAssessmentPrompt(subtask, dependencies);

  const requestBody = {
    model: CEREBRAS_MODEL,
    messages: [
      {
        role: "system" as const,
        content: "You are an expert software engineering risk analyst. Analyze development tasks and provide structured risk assessments in JSON format."
      },
      {
        role: "user" as const,
        content: prompt
      }
    ],
    temperature: 0.7,
    max_tokens: 2000,
  };

  try {
    const response = await fetch(CEREBRAS_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${CEREBRAS_API_KEY}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Cerebras API error: ${response.status} ${response.statusText} - ${errorText}`
      );
    }

    const data = await response.json();
    
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      throw new Error("Invalid response format from Cerebras API");
    }

    const content = data.choices[0].message.content;
    
    // Try to extract JSON from the response (might be wrapped in markdown code blocks)
    let jsonContent = content.trim();
    if (jsonContent.startsWith("```json")) {
      jsonContent = jsonContent.replace(/^```json\s*/, "").replace(/\s*```$/, "");
    } else if (jsonContent.startsWith("```")) {
      jsonContent = jsonContent.replace(/^```\s*/, "").replace(/\s*```$/, "");
    }

    const assessment = JSON.parse(jsonContent) as LLMRiskAssessment;

    // Validate the assessment structure
    if (!assessment.risk_level || !["low", "medium", "high"].includes(assessment.risk_level)) {
      throw new Error("Invalid risk_level in LLM response");
    }

    if (!Array.isArray(assessment.risk_factors)) {
      assessment.risk_factors = [];
    }

    // Validate risk factors
    assessment.risk_factors = assessment.risk_factors.filter((rf: RiskFactor) => {
      return rf.factor && rf.description && 
             ["low", "medium", "high"].includes(rf.severity);
    });

    return assessment;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error(`Failed to parse LLM response as JSON: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Generate default risk assessment as fallback.
 */
export function generateDefaultAssessment(
  subtask: Subtask
): LLMRiskAssessment {
  return {
    risk_level: "medium",
    risk_factors: [
      {
        factor: "unknown_complexity",
        description: "Unable to assess complexity due to LLM unavailability",
        severity: "medium",
      },
    ],
    mitigation_suggestions: "Review task requirements manually and break down into smaller subtasks if needed.",
    reasoning: "Default assessment generated due to LLM service unavailability",
  };
}

