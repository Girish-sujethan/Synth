import React, { useState, useEffect } from 'react';
import { Task, TaskUpdateRequest, AssigneeType } from '../types/task';
import { TagInput } from './TagInput';
import { SizePicker } from './SizePicker';
import { AssigneePicker } from './AssigneePicker';

interface TaskEditFormProps {
  task: Task;
  onSave: (data: TaskUpdateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string | null;
  availableColumns?: Array<{ id: string; key: string; name: string }>;
  canOverrideAssignment?: boolean;
  availableUsers?: Array<{ id: string; name: string }>;
  availableAgents?: Array<{ id: string; name: string }>;
  tagSuggestions?: string[];
}

export const TaskEditForm: React.FC<TaskEditFormProps> = ({
  task,
  onSave,
  onCancel,
  isLoading = false,
  error,
  availableColumns = [],
  canOverrideAssignment = false,
  availableUsers = [],
  availableAgents = [],
  tagSuggestions = [],
}) => {
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [tags, setTags] = useState<string[]>(task.tags || []);
  const [size, setSize] = useState<number | undefined>(task.size);
  const [assigneeType, setAssigneeType] = useState<AssigneeType | undefined>(task.assignee_type);
  const [assigneeId, setAssigneeId] = useState<string | undefined>(task.assignee_id);
  const [columnKey, setColumnKey] = useState<string | undefined>(task.column_key);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Track if form has changes
  const hasChanges =
    title !== task.title ||
    description !== (task.description || '') ||
    JSON.stringify(tags.sort()) !== JSON.stringify((task.tags || []).sort()) ||
    size !== task.size ||
    assigneeType !== task.assignee_type ||
    assigneeId !== task.assignee_id ||
    columnKey !== task.column_key;

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!title.trim()) {
      errors.title = 'Title is required';
    }

    if (size !== undefined && ![1, 2, 3, 5, 8, 13].includes(size)) {
      errors.size = 'Size must be a Fibonacci number (1, 2, 3, 5, 8, 13)';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      const updateData: TaskUpdateRequest = {
        title: title !== task.title ? title : undefined,
        description: description !== (task.description || '') ? description : undefined,
        tags: JSON.stringify(tags.sort()) !== JSON.stringify((task.tags || []).sort()) ? tags : undefined,
        size: size !== task.size ? size : undefined,
        assignee_type: assigneeType !== task.assignee_type ? assigneeType : undefined,
        assignee_id: assigneeId !== task.assignee_id ? assigneeId : undefined,
        column_key: columnKey !== task.column_key ? columnKey : undefined,
      };

      // Remove undefined fields
      Object.keys(updateData).forEach((key) => {
        if (updateData[key as keyof TaskUpdateRequest] === undefined) {
          delete updateData[key as keyof TaskUpdateRequest];
        }
      });

      await onSave(updateData);
    } catch (err) {
      // Error handling is done by parent component
      console.error('Save failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Edit Task</h3>
        <button
          type="button"
          onClick={onCancel}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          Cancel
        </button>
      </div>

      {/* Title */}
      <div>
        <label htmlFor="edit-title" className="block text-sm font-medium text-gray-700 mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="edit-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            validationErrors.title ? 'border-red-500' : ''
          }`}
          required
        />
        {validationErrors.title && (
          <p className="mt-1 text-sm text-red-600">{validationErrors.title}</p>
        )}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="edit-description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="edit-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {/* Size */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Size (Fibonacci)
        </label>
        <SizePicker value={size} onChange={setSize} disabled={isLoading} />
        {validationErrors.size && (
          <p className="mt-1 text-sm text-red-600">{validationErrors.size}</p>
        )}
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tags
        </label>
        <TagInput
          tags={tags}
          onChange={setTags}
          suggestions={tagSuggestions}
          disabled={isLoading}
        />
      </div>

      {/* Column */}
      {availableColumns.length > 0 && (
        <div>
          <label htmlFor="edit-column" className="block text-sm font-medium text-gray-700 mb-1">
            Column
          </label>
          <select
            id="edit-column"
            value={columnKey || ''}
            onChange={(e) => setColumnKey(e.target.value || undefined)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">No column</option>
            {availableColumns.map((col) => (
              <option key={col.key} value={col.key}>
                {col.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Assignee (only for managers/admins) */}
      {canOverrideAssignment && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Assignment Override
          </label>
          <AssigneePicker
            assigneeType={assigneeType}
            assigneeId={assigneeId}
            onChange={(type, id) => {
              setAssigneeType(type);
              setAssigneeId(id);
            }}
            availableUsers={availableUsers}
            availableAgents={availableAgents}
            disabled={isLoading}
          />
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 border border-gray-300"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={!hasChanges || isLoading}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {isLoading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
};
