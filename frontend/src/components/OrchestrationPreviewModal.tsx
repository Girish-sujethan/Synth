import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

const getAuthToken = () => {
  return localStorage.getItem('auth_token') || '';
};

interface AssignmentPreview {
  subtask_index: number;
  assignee_type: 'human' | 'ai';
  assignee_id: string;
  assignment_risk: 'low' | 'medium' | 'high';
  reasoning: string;
}

interface OrchestrationPreviewModalProps {
  taskId: string;
  teamId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  subtasks: Array<{ id: string; title: string; tags: string[] }>;
  teamMembers: Array<{ user_id: string; name: string; level?: string }>;
  aiAgents: Array<{ id: string; name: string }>;
}

export const OrchestrationPreviewModal: React.FC<OrchestrationPreviewModalProps> = ({
  taskId,
  teamId,
  isOpen,
  onClose,
  onSuccess,
  subtasks,
  teamMembers,
  aiAgents,
}) => {
  const [assignments, setAssignments] = useState<AssignmentPreview[]>([]);
  const [policyVersion, setPolicyVersion] = useState<string>('');
  const [model, setModel] = useState<string>('');
  const [strategy, setStrategy] = useState<string>('balanced');
  const [instructions, setInstructions] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGeneratePreview = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = getAuthToken();
      const response = await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/orchestrate/preview`,
        {
          strategy: strategy,
          instructions: instructions || undefined,
        },
        {
          params: { team_id: teamId },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setAssignments(response.data.assignments || []);
      setPolicyVersion(response.data.policy_version || '');
      setModel(response.data.model || '');
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to generate orchestration preview';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    setIsConfirming(true);
    setError(null);

    try {
      const token = getAuthToken();
      await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/orchestrate/confirm`,
        {
          assignments: assignments,
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
        'Failed to confirm orchestration';
      setError(errorMessage);
    } finally {
      setIsConfirming(false);
    }
  };

  const getAssigneeName = (assignment: AssignmentPreview): string => {
    if (assignment.assignee_type === 'human') {
      const member = teamMembers.find((m) => m.user_id === assignment.assignee_id);
      return member?.name || assignment.assignee_id;
    } else {
      const agent = aiAgents.find((a) => a.id === assignment.assignee_id);
      return agent?.name || assignment.assignee_id;
    }
  };

  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Task Orchestration Preview</h3>
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
                <p className="mt-2 text-sm text-gray-600">Generating assignments with AI...</p>
              </div>
            ) : assignments.length > 0 ? (
              <div className="space-y-6">
                <div className="text-sm text-gray-600">
                  <p>
                    <strong>Policy Version:</strong> {policyVersion}
                  </p>
                  <p>
                    <strong>Model:</strong> {model}
                  </p>
                  <p>
                    <strong>Strategy:</strong> {strategy}
                  </p>
                  <p className="mt-2 text-amber-600">
                    ⚠️ This is a preview. Assignments will not be applied until you confirm.
                  </p>
                </div>

                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {assignments.map((assignment, index) => {
                    const subtask = subtasks[assignment.subtask_index - 1];
                    return (
                      <div
                        key={index}
                        className="p-4 border border-gray-200 rounded-lg bg-gray-50"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-medium text-gray-900">
                              {subtask ? subtask.title : `Subtask ${assignment.subtask_index}`}
                            </h4>
                            <p className="text-sm text-gray-500">
                              Tags: {subtask?.tags.join(', ') || 'N/A'}
                            </p>
                          </div>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getRiskColor(
                              assignment.assignment_risk
                            )}`}
                          >
                            {assignment.assignment_risk} risk
                          </span>
                        </div>

                        <div className="mt-3 space-y-2">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-700">Assignee:</span>
                            <span className="text-sm text-gray-900">
                              {getAssigneeName(assignment)} ({assignment.assignee_type})
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-700">Reasoning:</span>
                            <p className="text-sm text-gray-600 mt-1">{assignment.reasoning}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
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
                    disabled={isConfirming || assignments.length === 0}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isConfirming ? 'Confirming...' : 'Confirm Assignments'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Strategy
                  </label>
                  <select
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="balanced">Balanced</option>
                    <option value="speed">Speed</option>
                    <option value="quality">Quality</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Optional Instructions
                  </label>
                  <textarea
                    value={instructions}
                    onChange={(e) => setInstructions(e.target.value)}
                    rows={3}
                    placeholder="Provide any specific instructions for task assignment..."
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
