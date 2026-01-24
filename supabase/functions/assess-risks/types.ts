/** TypeScript type definitions for risk assessment Edge Function. */

export interface Subtask {
  id: string;
  description: string;
  dependencies?: string[];
}

export interface Dependency {
  id: string;
  type: string;
  description?: string;
}

export interface RiskAssessmentRequest {
  task_id: number;
  subtasks: Subtask[];
  dependencies?: Dependency[];
}

export interface RiskFactor {
  factor: string;
  description: string;
  severity: "low" | "medium" | "high";
}

export interface LLMRiskAssessment {
  risk_level: "low" | "medium" | "high";
  risk_factors: RiskFactor[];
  mitigation_suggestions: string;
  reasoning: string;
}

export interface CerebrasAPIRequest {
  model: string;
  messages: Array<{
    role: "system" | "user" | "assistant";
    content: string;
  }>;
  temperature?: number;
  max_tokens?: number;
}

export interface CerebrasAPIResponse {
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface AssessmentResult {
  subtask_id: string;
  assessment: LLMRiskAssessment;
  reasoning_trace_id?: number;
}

