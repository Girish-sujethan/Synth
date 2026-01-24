import React, { useState } from 'react';
import { BoardColumn } from './KanbanBoard';

interface TaskMoveControlProps {
  currentColumnKey?: string;
  columns: BoardColumn[];
  onMove: (columnKey: string) => Promise<void>;
  isLoading?: boolean;
  showQuickActions?: boolean;
  taskAssigneeType?: string;
  taskTags?: string[];
}

export const TaskMoveControl: React.FC<TaskMoveControlProps> = ({
  currentColumnKey,
  columns,
  onMove,
  isLoading = false,
  showQuickActions = false,
  taskAssigneeType,
  taskTags = [],
}) => {
  const [error, setError] = useState<string | null>(null);
  const availableColumns = columns.filter((col) => col.key !== currentColumnKey && !col.is_locked);

  const handleMove = async (columnKey: string) => {
    setError(null);
    try {
      await onMove(columnKey);
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to move task';
      setError(errorMessage);
    }
  };

  // Find common column keys
  const reviewColumn = columns.find((col) => col.key === 'review' || col.name.toLowerCase() === 'review');
  const doneColumn = columns.find((col) => col.key === 'done' || col.name.toLowerCase() === 'done');
  const nextColumn = columns.find((col, idx) => {
    const currentIdx = columns.findIndex((c) => c.key === currentColumnKey);
    return currentIdx >= 0 && idx === currentIdx + 1;
  });
  const prevColumn = columns.find((col, idx) => {
    const currentIdx = columns.findIndex((c) => c.key === currentColumnKey);
    return currentIdx > 0 && idx === currentIdx - 1;
  });

  const isAIAssigned = taskAssigneeType === 'ai' || taskAssigneeType === 'agent';
  const hasReviewTags = taskTags.some((tag) =>
    ['review-required', 'approval-required', 'high-risk'].includes(tag.toLowerCase())
  );

  if (availableColumns.length === 0) {
    return (
      <div className="text-xs text-gray-500">No other columns available</div>
    );
  }

  return (
    <div className="space-y-3">
      {showQuickActions && (
        <div className="flex flex-wrap gap-2">
          {prevColumn && (
            <button
              type="button"
              onClick={() => handleMove(prevColumn.key)}
              disabled={isLoading}
              className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
            >
              ← Previous
            </button>
          )}
          {nextColumn && (
            <button
              type="button"
              onClick={() => handleMove(nextColumn.key)}
              disabled={isLoading}
              className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
            >
              Next →
            </button>
          )}
          {reviewColumn && reviewColumn.key !== currentColumnKey && (
            <button
              type="button"
              onClick={() => handleMove(reviewColumn.key)}
              disabled={isLoading}
              className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 disabled:opacity-50"
            >
              Move to Review
            </button>
          )}
          {doneColumn && doneColumn.key !== currentColumnKey && (
            <button
              type="button"
              onClick={() => handleMove(doneColumn.key)}
              disabled={isLoading || (isAIAssigned && !reviewColumn)}
              className="px-3 py-1.5 text-xs font-medium text-green-700 bg-green-100 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
              title={
                isAIAssigned && !reviewColumn
                  ? 'AI-assigned tasks must go through review first'
                  : undefined
              }
            >
              Move to Done
            </button>
          )}
          {isAIAssigned && (
            <button
              type="button"
              onClick={() => reviewColumn && handleMove(reviewColumn.key)}
              disabled={isLoading || !reviewColumn}
              className="px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-100 rounded hover:bg-purple-200 disabled:opacity-50"
            >
              Approve
            </button>
          )}
        </div>
      )}

      <div className="flex items-center gap-2">
        <label htmlFor="move-column" className="text-sm font-medium text-gray-700">
          Move to:
        </label>
        <select
          id="move-column"
          value=""
          onChange={(e) => {
            if (e.target.value) {
              handleMove(e.target.value);
            }
          }}
          disabled={isLoading}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:opacity-50"
          aria-label="Select column to move task to"
        >
          <option value="">Select column...</option>
          {availableColumns.map((col) => (
            <option key={col.id} value={col.key}>
              {col.display_name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-2 text-xs text-red-800" role="alert">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="text-xs text-gray-500">Moving task...</div>
      )}
    </div>
  );
};

