import React from 'react';
import { Task } from '../types/task';
import { TagChips } from './TagChips';
import { StatusChip } from './StatusChip';

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
  isSubtask?: boolean;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onClick, isSubtask = false }) => {
  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const cardClasses = `
    bg-white rounded-lg shadow-sm border border-gray-200 p-4
    ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}
    ${isSubtask ? 'ml-4 border-l-4 border-l-blue-300' : ''}
  `.trim();

  return (
    <div
      className={cardClasses}
      onClick={handleClick}
      role={onClick ? 'button' : 'article'}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleClick();
              }
            }
          : undefined
      }
      aria-label={`Task: ${task.title}`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className={`font-semibold text-gray-900 line-clamp-2 flex-1 ${isSubtask ? 'text-sm' : ''}`}>
          {task.title}
        </h3>
        {task.column_key && (
          <StatusChip columnKey={task.column_key} className="flex-shrink-0" />
        )}
      </div>

      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{task.description}</p>
      )}

      {/* Size indicator */}
      {task.size && (
        <div className="mb-2">
          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
            Size: {task.size}
          </span>
        </div>
      )}

      <div className="flex items-center justify-between flex-wrap gap-2">
        <TagChips
          tags={task.tags}
          assigneeType={task.assignee_type}
          risk={task.assignment_risk}
        />

        {task.subtask_count > 0 && !isSubtask && (
          <span
            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            title={`${task.subtask_count} subtask${task.subtask_count !== 1 ? 's' : ''}`}
            aria-label={`${task.subtask_count} subtask${task.subtask_count !== 1 ? 's' : ''}`}
          >
            {task.subtask_count} subtask{task.subtask_count !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Subtask-specific info: assignee and status */}
      {isSubtask && (
        <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
          {task.assignee_display_name && (
            <span>Assigned to: {task.assignee_display_name}</span>
          )}
          {task.column_key && (
            <span className="ml-auto">Status: {task.column_key}</span>
          )}
        </div>
      )}
    </div>
  );
};
