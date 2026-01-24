import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { SizePicker } from './SizePicker';
import { TagInput } from './TagInput';

const API_BASE_URL = '/api';

const getAuthToken = () => {
  return localStorage.getItem('auth_token') || '';
};

interface SubtaskPreview {
  title: string;
  description: string;
  size: number;
  tags: string[];
}

interface SplitTaskModalProps {
  taskId: string;
  teamId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const SENIORITY_TAGS = ['intern', 'junior', 'mid', 'senior'];
const VALID_SIZES = [1, 2, 3, 5, 8];

export const SplitTaskModal: React.FC<SplitTaskModalProps> = ({
  taskId,
  teamId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [subtasks, setSubtasks] = useState<SubtaskPreview[]>([]);
  const [policyVersion, setPolicyVersion] = useState<string>('');
  const [model, setModel] = useState<string>('');
  const [instructions, setInstructions] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<number, string[]>>({});

  useEffect(() => {
    if (isOpen && subtasks.length === 0) {
      handleGeneratePreview();
    }
  }, [isOpen]);

  const validateSubtask = (subtask: SubtaskPreview, index: number): string[] => {
    const errors: string[] = [];

    if (!subtask.title.trim()) {
      errors.push('Title is required');
    }

    if (!subtask.description.trim()) {
      errors.push('Description is required');
    }

    if (!VALID_SIZES.includes(subtask.size)) {
      errors.push(`Size must be one of: ${VALID_SIZES.join(', ')}`);
    }

    const seniorityTags = subtask.tags.filter((tag) => SENIORITY_TAGS.includes(tag));
    if (seniorityTags.length !== 1) {
      errors.push('Must have exactly one seniority tag (intern, junior, mid, or senior)');
    }

    const skillTags = subtask.tags.filter((tag) => !SENIORITY_TAGS.includes(tag));
    if (skillTags.length === 0) {
      errors.push('Must have at least one skill tag');
    }

    // Check for duplicate titles
    const duplicateIndex = subtasks.findIndex(
      (st, idx) => idx !== index && st.title.trim().toLowerCase() === subtask.title.trim().toLowerCase()
    );
    if (duplicateIndex !== -1) {
      errors.push('Title must be unique');
    }

    return errors;
  };

  const validateAllSubtasks = (): boolean => {
    const errors: Record<number, string[]> = {};
    let isValid = true;

    subtasks.forEach((subtask, index) => {
      const subtaskErrors = validateSubtask(subtask, index);
      if (subtaskErrors.length > 0) {
        errors[index] = subtaskErrors;
        isValid = false;
      }
    });

    setValidationErrors(errors);
    return isValid;
  };

  const handleGeneratePreview = async () => {
    setIsLoading(true);
    setError(null);
    setValidationErrors({});

    try {
      const token = getAuthToken();
      const response = await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/split`,
        {
          instructions: instructions || undefined,
        },
        {
          params: { team_id: teamId },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setSubtasks(response.data.subtasks || []);
      setPolicyVersion(response.data.policy_version || '');
      setModel(response.data.model || '');
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to generate subtask preview';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!validateAllSubtasks()) {
      setError('Please fix validation errors before confirming');
      return;
    }

    setIsConfirming(true);
    setError(null);

    try {
      const token = getAuthToken();
      await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/split/confirm`,
        {
          subtasks: subtasks,
        },
        {
          params: { team_id: teamId },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      onSuccess();
      onClose();
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to confirm task split';
      setError(errorMessage);
    } finally {
      setIsConfirming(false);
    }
  };

  const handleSubtaskChange = (index: number, field: keyof SubtaskPreview, value: any) => {
    const updated = [...subtasks];
    updated[index] = { ...updated[index], [field]: value };
    setSubtasks(updated);

    // Clear validation errors for this subtask
    if (validationErrors[index]) {
      const newErrors = { ...validationErrors };
      delete newErrors[index];
      setValidationErrors(newErrors);
    }
  };

  const handleRemoveSubtask = (index: number) => {
    setSubtasks(subtasks.filter((_, i) => i !== index));
    const newErrors = { ...validationErrors };
    delete newErrors[index];
    // Reindex remaining errors
    const reindexed: Record<number, string[]> = {};
    Object.keys(newErrors).forEach((key) => {
      const oldIndex = parseInt(key);
      if (oldIndex > index) {
        reindexed[oldIndex - 1] = newErrors[oldIndex];
      } else if (oldIndex < index) {
        reindexed[oldIndex] = newErrors[oldIndex];
      }
    });
    setValidationErrors(reindexed);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Split Task into Subtasks</h3>
              <button
                type="button"
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 focus:outline-none"
              >
                <span className="sr-only">Close</span>
                ×
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {isLoading ? (
              <div className="py-8 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-sm text-gray-600">Generating subtasks with AI...</p>
              </div>
            ) : subtasks.length > 0 ? (
              <div className="space-y-6">
                <div className="text-sm text-gray-600">
                  <p>
                    <strong>Policy Version:</strong> {policyVersion}
                  </p>
                  <p>
                    <strong>Model:</strong> {model}
                  </p>
                  <p className="mt-2 text-amber-600">
                    ⚠️ This is a preview. Subtasks will not be created until you confirm.
                  </p>
                </div>

                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {subtasks.map((subtask, index) => (
                    <div
                      key={index}
                      className="p-4 border border-gray-200 rounded-lg bg-gray-50"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900">Subtask {index + 1}</h4>
                        <button
                          type="button"
                          onClick={() => handleRemoveSubtask(index)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Remove
                        </button>
                      </div>

                      {validationErrors[index] && (
                        <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-sm">
                          <ul className="list-disc list-inside text-red-800">
                            {validationErrors[index].map((err, errIdx) => (
                              <li key={errIdx}>{err}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Title *
                          </label>
                          <input
                            type="text"
                            value={subtask.title}
                            onChange={(e) => handleSubtaskChange(index, 'title', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Description *
                          </label>
                          <textarea
                            value={subtask.description}
                            onChange={(e) => handleSubtaskChange(index, 'description', e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Size *
                          </label>
                          <SizePicker
                            value={subtask.size}
                            onChange={(size) => handleSubtaskChange(index, 'size', size || 1)}
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Tags * (must include exactly one seniority tag and at least one skill tag)
                          </label>
                          <TagInput
                            tags={subtask.tags}
                            onChange={(tags) => handleSubtaskChange(index, 'tags', tags)}
                            suggestions={[...SENIORITY_TAGS, 'python', 'javascript', 'api', 'frontend', 'backend', 'database', 'testing']}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-end space-x-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirm}
                    disabled={isConfirming || subtasks.length === 0}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isConfirming ? 'Confirming...' : 'Confirm Split'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Optional Instructions
                  </label>
                  <textarea
                    value={instructions}
                    onChange={(e) => setInstructions(e.target.value)}
                    rows={3}
                    placeholder="Provide any specific instructions for how to split this task..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex items-center justify-end space-x-3">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleGeneratePreview}
                    disabled={isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    Generate Preview
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
