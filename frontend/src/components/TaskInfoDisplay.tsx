import React, { useState, useEffect } from 'react';
import { Task } from '../types/task';
import { TagChips } from './TagChips';
import { TaskEditForm } from './TaskEditForm';
import { TaskUpdateRequest } from '../types/task';

interface TaskInfoDisplayProps {
  task: Task;
  canEdit: boolean;
  onSave: (data: TaskUpdateRequest) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  availableColumns?: Array<{ id: string; key: string; name: string }>;
  canOverrideAssignment?: boolean;
  availableUsers?: Array<{ id: string; name: string }>;
  availableAgents?: Array<{ id: string; name: string }>;
  tagSuggestions?: string[];
}

export const TaskInfoDisplay: React.FC<TaskInfoDisplayProps> = ({
  task,
  canEdit,
  onSave,
  isLoading = false,
  error,
  availableColumns = [],
}) => {
  const [isEditing, setIsEditing] = useState(false);

  if (isEditing) {
    return (
      <TaskEditForm
        task={task}
        onSave={async (data) => {
          await onSave(data);
          setIsEditing(false);
        }}
        onCancel={() => setIsEditing(false)}
        isLoading={isLoading}
        error={error}
        availableColumns={availableColumns}
        canOverrideAssignment={canOverrideAssignment}
        availableUsers={availableUsers}
        availableAgents={availableAgents}
        tagSuggestions={tagSuggestions}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-500">Title</h3>
          {canEdit && (
            <button
              onClick={() => setIsEditing(true)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Edit
            </button>
          )}
        </div>
        <p className="text-base font-semibold text-gray-900">{task.title}</p>
      </div>

      {/* Description */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-500">Description</h3>
          {canEdit && (
            <button
              onClick={() => setIsEditing(true)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Edit
            </button>
          )}
        </div>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-700 whitespace-pre-wrap">
            {task.description || 'No description provided.'}
          </p>
        </div>
      </div>

      {/* Size Estimate */}
      {task.size && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Size Estimate</h3>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            {task.size} {task.size === 1 ? 'point' : 'points'} (Fibonacci)
          </div>
        </div>
      )}

      {/* Tags */}
      <div>
        <h3 className="text-sm font-medium text-gray-500 mb-2">Tags</h3>
        <TagChips
          tags={task.tags}
          assigneeType={task.assignee_type}
          risk={task.assignment_risk}
        />
      </div>

      {/* Assignee Information */}
      <div>
        <h3 className="text-sm font-medium text-gray-500 mb-2">Assignment</h3>
        <div className="space-y-2">
          <div>
            <span className="text-sm text-gray-600">Assignee Type: </span>
            <span className="text-sm font-medium text-gray-900 capitalize">
              {task.assignee_type || 'Unassigned'}
            </span>
            {task.assignee_type && (
              <span className="ml-2">
                {task.assignee_type === 'ai' ? '🤖' : task.assignee_type === 'human' ? '@' : ''}
              </span>
            )}
          </div>
          {task.assignee_id && (
            <div>
              <span className="text-sm text-gray-600">Assignee ID: </span>
              <span className="text-sm text-gray-900">{task.assignee_id}</span>
            </div>
          )}
          {task.assignment_risk && (
            <div>
              <span className="text-sm text-gray-600">Assignment Risk: </span>
              <span
                className={`text-sm font-medium capitalize ${
                  task.assignment_risk === 'high'
                    ? 'text-red-600'
                    : task.assignment_risk === 'medium'
                    ? 'text-yellow-600'
                    : 'text-green-600'
                }`}
              >
                {task.assignment_risk}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Status */}
      {task.status && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
          <span className="inline-flex items-center px-2 py-1 rounded text-sm font-medium bg-gray-100 text-gray-700">
            {task.status}
          </span>
        </div>
      )}

      {/* Column */}
      {task.column_key && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Column</h3>
          <span className="inline-flex items-center px-2 py-1 rounded text-sm font-medium bg-gray-100 text-gray-700">
            {task.column_key}
          </span>
        </div>
      )}
    </div>
  );
};
