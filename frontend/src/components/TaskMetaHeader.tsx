import React from 'react';
import { Task, AssigneeType } from '../types/task';
import { StatusChip } from './StatusChip';
import { BoardColumn } from './KanbanBoard';

interface TaskMetaHeaderProps {
  task: Task;
  columns?: BoardColumn[];
}

export const TaskMetaHeader: React.FC<TaskMetaHeaderProps> = ({ task, columns = [] }) => {
  const getAssigneeChip = () => {
    if (!task.assignee_type || task.assignee_type === AssigneeType.UNASSIGNED) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          Unassigned
        </span>
      );
    }

    if (task.assignee_type === AssigneeType.AI) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          <span className="mr-1">🤖</span>
          Agent {task.assignee_id ? `(${task.assignee_id.slice(0, 8)}...)` : ''}
        </span>
      );
    }

    if (task.assignee_type === AssigneeType.HUMAN) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <span className="mr-1">@</span>
          Human {task.assignee_id ? `(${task.assignee_id.slice(0, 8)}...)` : ''}
        </span>
      );
    }

    return null;
  };

  return (
    <div className="space-y-3">
      {/* Title */}
      <h2 className="text-2xl font-semibold text-gray-900">{task.title}</h2>

      {/* Status and Assignee Row */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Status */}
        {task.column_key && (
          <StatusChip
            columnKey={task.column_key}
            displayName={
              columns.find((c) => c.key === task.column_key)?.display_name
            }
          />
        )}

        {/* Assignee Chip */}
        {getAssigneeChip()}
      </div>
    </div>
  );
};
