import React from 'react';
import { Task } from '../types/task';

interface HierarchySectionProps {
  task: Task;
  parentTitle?: string;
  subtasksPreview?: Array<{
    id: string;
    title: string;
    column_key?: string;
    assignee_display_name?: string;
  }>;
  onParentClick?: (parentId: string) => void;
  onSubtaskClick?: (subtaskId: string) => void;
}

export const HierarchySection: React.FC<HierarchySectionProps> = ({
  task,
  parentTitle,
  subtasksPreview,
  onParentClick,
  onSubtaskClick,
}) => {
  // If this is a subtask, show parent link
  if (task.parent_id) {
    return (
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Parent Task</h3>
        {onParentClick ? (
          <button
            onClick={() => onParentClick(task.parent_id!)}
            className="text-sm text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
          >
            <span>←</span>
            <span>{parentTitle || `Task ${task.parent_id.slice(0, 8)}...`}</span>
          </button>
        ) : (
          <p className="text-sm text-blue-700">
            {parentTitle || `Parent: ${task.parent_id.slice(0, 8)}...`}
          </p>
        )}
      </div>
    );
  }

  // If this is a parent task, show subtasks preview
  if (task.subtask_count > 0) {
    return (
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Subtasks ({task.subtask_count})
        </h3>
        {subtasksPreview && subtasksPreview.length > 0 ? (
          <div className="space-y-2">
            {subtasksPreview.map((subtask) => (
              <div
                key={subtask.id}
                className="bg-gray-50 rounded-lg p-3 border border-gray-200 hover:bg-gray-100 transition-colors"
              >
                {onSubtaskClick ? (
                  <button
                    onClick={() => onSubtaskClick(subtask.id)}
                    className="text-left w-full"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {subtask.title}
                        </p>
                        {subtask.assignee_display_name && (
                          <p className="text-xs text-gray-500 mt-1">
                            {subtask.assignee_display_name}
                          </p>
                        )}
                      </div>
                      {subtask.column_key && (
                        <span className="ml-2 text-xs text-gray-500 flex-shrink-0">
                          {subtask.column_key}
                        </span>
                      )}
                    </div>
                  </button>
                ) : (
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {subtask.title}
                      </p>
                      {subtask.assignee_display_name && (
                        <p className="text-xs text-gray-500 mt-1">
                          {subtask.assignee_display_name}
                        </p>
                      )}
                    </div>
                    {subtask.column_key && (
                      <span className="ml-2 text-xs text-gray-500 flex-shrink-0">
                        {subtask.column_key}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            This task has {task.subtask_count} subtask{task.subtask_count !== 1 ? 's' : ''}.
          </p>
        )}
      </div>
    );
  }

  // No hierarchy
  return null;
};
