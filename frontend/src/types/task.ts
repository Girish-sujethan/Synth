export enum AssigneeType {
  HUMAN = 'human',
  AI = 'ai',
  UNASSIGNED = 'unassigned',
}

export enum AssignmentRisk {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export enum TaskSize {
  ONE = 1,
  TWO = 2,
  THREE = 3,
  FIVE = 5,
  EIGHT = 8,
}

export interface Task {
  id: string;
  team_id: string;
  parent_id?: string;
  title: string;
  description?: string;
  status?: string;
  size?: number; // Fibonacci: 1, 2, 3, 5, 8
  tags: string[];
  column_id?: string;
  column_key?: string;
  assignee_type?: AssigneeType;
  assignee_id?: string;
  assignment_risk?: AssignmentRisk;
  assignment_reason?: string; // From TaskDetailResponse
  override_flag: boolean;
  subtask_count: number;
  created_at: string;
  updated_at: string;
  // Additional fields from TaskDetailResponse
  assignee_display_name?: string;
  parent_title?: string;
  subtasks_preview?: Array<{
    id: string;
    title: string;
    column_key?: string;
    assignee_display_name?: string;
  }>;
  audit_history?: Array<{
    id: string;
    event_type: string;
    created_at: string;
    user_id?: string;
    payload: Record<string, any>;
  }>;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  parent_id?: string;
  size?: number;
  tags?: string[];
  column_key?: string;
  assignee_type?: AssigneeType;
  assignee_id?: string;
  assignment_risk?: AssignmentRisk;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  status?: string;
  size?: number;
  tags?: string[];
  column_key?: string;
  assignee_type?: AssigneeType;
  assignee_id?: string;
  assignment_risk?: AssignmentRisk;
  override_flag?: boolean;
}
