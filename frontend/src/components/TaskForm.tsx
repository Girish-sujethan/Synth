import React, { useEffect, useState } from 'react';
import { Task, TaskCreateRequest, TaskUpdateRequest, TaskSize, AssigneeType, AssignmentRisk } from '../types/task';

// Fix for axios error type
interface AxiosError {
  message?: string;
  response?: {
    data?: {
      error?: {
        message?: string;
      };
    };
  };
}

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskCreateRequest | TaskUpdateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string | null;
  availableColumns?: Array<{ id: string; key: string; name: string }>;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  task,
  onSubmit,
  onCancel,
  isLoading = false,
  error,
  availableColumns = [],
}) => {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [tags, setTags] = useState<string[]>(task?.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [size, setSize] = useState<number | undefined>(task?.size);
  const [columnKey, setColumnKey] = useState(task?.column_key || '');
  const [assigneeType, setAssigneeType] = useState<AssigneeType | undefined>(task?.assignee_type);
  const [assigneeId, setAssigneeId] = useState(task?.assignee_id || '');
  const [assignmentRisk, setAssignmentRisk] = useState<AssignmentRisk | undefined>(task?.assignment_risk);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || '');
      setTags(task.tags || []);
      setSize(task.size);
      setColumnKey(task.column_key || '');
      setAssigneeType(task.assignee_type);
      setAssigneeId(task.assignee_id || '');
      setAssignmentRisk(task.assignment_risk);
    }
  }, [task]);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!title.trim()) {
      errors.title = 'Title is required';
    }

    if (size !== undefined && !Object.values(TaskSize).includes(size as TaskSize)) {
      errors.size = 'Size must be 1, 2, 3, 5, or 8 (Fibonacci)';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const formData: TaskCreateRequest | TaskUpdateRequest = {
      title: title.trim(),
      description: description.trim() || undefined,
      tags: tags.length > 0 ? tags.map(t => t.toLowerCase()) : undefined,
      size: size,
      column_key: columnKey || undefined,
      assignee_type: assigneeType,
      assignee_id: assigneeId || undefined,
      assignment_risk: assignmentRisk,
    };

    await onSubmit(formData);
  };

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" aria-label={task ? 'Edit task' : 'Create task'}>
      {error && (
        <div className="rounded-md bg-red-50 p-4" role="alert">
          <div className="text-sm text-red-800">{error}</div>
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            validationErrors.title ? 'border-red-500' : ''
          }`}
          required
          aria-invalid={!!validationErrors.title}
          aria-describedby={validationErrors.title ? 'title-error' : undefined}
        />
        {validationErrors.title && (
          <p id="title-error" className="mt-1 text-sm text-red-600" role="alert">
            {validationErrors.title}
          </p>
        )}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {/* Size (Fibonacci) */}
      <div>
        <label htmlFor="size" className="block text-sm font-medium text-gray-700">
          Size (Fibonacci: 1, 2, 3, 5, 8)
        </label>
        <select
          id="size"
          value={size || ''}
          onChange={(e) => setSize(e.target.value ? Number(e.target.value) : undefined)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Select size</option>
          {Object.values(TaskSize).filter(v => typeof v === 'number').map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        {validationErrors.size && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {validationErrors.size}
          </p>
        )}
      </div>

      {/* Column */}
      {availableColumns.length > 0 && (
        <div>
          <label htmlFor="column" className="block text-sm font-medium text-gray-700">
            Column
          </label>
          <select
            id="column"
            value={columnKey}
            onChange={(e) => setColumnKey(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Select column</option>
            {availableColumns.map((col) => (
              <option key={col.id} value={col.key || col.name}>
                {col.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Tags */}
      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
          Tags
        </label>
        <div className="mt-1 flex gap-2">
          <input
            type="text"
            id="tags"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagInputKeyDown}
            placeholder="Add tag and press Enter"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="text-blue-600 hover:text-blue-800"
                  aria-label={`Remove tag ${tag}`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Assignee Type */}
      <div>
        <label htmlFor="assignee_type" className="block text-sm font-medium text-gray-700">
          Assignee Type
        </label>
        <select
          id="assignee_type"
          value={assigneeType || ''}
          onChange={(e) => setAssigneeType(e.target.value as AssigneeType | undefined)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Unassigned</option>
          <option value={AssigneeType.HUMAN}>Human</option>
          <option value={AssigneeType.AI}>AI</option>
        </select>
      </div>

      {/* Assignee ID */}
      {assigneeType && (
        <div>
          <label htmlFor="assignee_id" className="block text-sm font-medium text-gray-700">
            Assignee ID
          </label>
          <input
            type="text"
            id="assignee_id"
            value={assigneeId}
            onChange={(e) => setAssigneeId(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      )}

      {/* Assignment Risk */}
      <div>
        <label htmlFor="assignment_risk" className="block text-sm font-medium text-gray-700">
          Assignment Risk
        </label>
        <select
          id="assignment_risk"
          value={assignmentRisk || ''}
          onChange={(e) => setAssignmentRisk(e.target.value as AssignmentRisk | undefined)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Select risk level</option>
          <option value={AssignmentRisk.LOW}>Low</option>
          <option value={AssignmentRisk.MEDIUM}>Medium</option>
          <option value={AssignmentRisk.HIGH}>High</option>
        </select>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : task ? 'Update Task' : 'Create Task'}
        </button>
      </div>
    </form>
  );
};
