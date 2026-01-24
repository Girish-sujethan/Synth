/**
 * TypeScript interfaces for risk assessment data structures.
 */

/**
 * Risk level enumeration.
 */
export type RiskLevel = "low" | "medium" | "high";

/**
 * Risk factor object structure.
 */
export interface RiskFactor {
  factor: string;
  description: string;
  severity: "low" | "medium" | "high";
}

/**
 * Individual assessment item.
 */
export interface AssessmentItem {
  id: number;
  subtask_id: string | null;
  risk_level: RiskLevel;
  risk_factors: RiskFactor[] | null;
  mitigation_suggestions: string | null;
}

/**
 * Risk assessment response from API.
 */
export interface RiskAssessmentResponse {
  task_id: number;
  assessments: AssessmentItem[];
  created_at: string;
}

/**
 * Assess risks request response.
 */
export interface AssessRisksResponse {
  task_id: number;
  status: string;
}

/**
 * Task information.
 */
export interface Task {
  id: number;
  description: string;
  status: string | null;
  created_at: string;
  updated_at: string;
}

