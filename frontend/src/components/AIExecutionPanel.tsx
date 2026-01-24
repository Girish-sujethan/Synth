import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

const getAuthToken = () => {
  return localStorage.getItem('auth_token') || '';
};

interface AIExecutionPanelProps {
  taskId: string;
  teamId: string;
  isAIAssigned: boolean;
  executionStatus?: 'pending' | 'running' | 'completed' | 'rejected';
  output?: string;
  onStatusChange?: (status: string) => void;
}

export const AIExecutionPanel: React.FC<AIExecutionPanelProps> = ({
  taskId,
  teamId,
  isAIAssigned,
  executionStatus = 'pending',
  output,
  onStatusChange,
}) => {
  const [status, setStatus] = useState<string>(executionStatus);
  const [executionOutput, setExecutionOutput] = useState<string>(output || '');
  const [isRunning, setIsRunning] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [approvalComment, setApprovalComment] = useState<string>('');

  useEffect(() => {
    setStatus(executionStatus);
  }, [executionStatus]);

  useEffect(() => {
    setExecutionOutput(output || '');
  }, [output]);

  // Poll for status updates if running
  useEffect(() => {
    if (status === 'running') {
      const interval = setInterval(() => {
        // In a real implementation, this would poll the API for status
        // For now, we'll just update locally
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [status]);

  const handleRunAgent = async () => {
    setIsRunning(true);
    setError(null);

    try {
      const token = getAuthToken();
      await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/run-agent`,
        {},
        {
          params: { team_id: teamId },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setStatus('running');
      if (onStatusChange) {
        onStatusChange('running');
      }
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to start AI agent execution';
      setError(errorMessage);
    } finally {
      setIsRunning(false);
    }
  };

  const handleApprovalDecision = async (approved: boolean) => {
    setIsApproving(true);
    setError(null);

    try {
      const token = getAuthToken();
      await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/execution/decision`,
        {
          approved: approved,
          comment: approvalComment || undefined,
        },
        {
          params: { team_id: teamId },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setStatus(approved ? 'completed' : 'rejected');
      if (onStatusChange) {
        onStatusChange(approved ? 'completed' : 'rejected');
      }
      setApprovalComment('');
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.error?.message ||
        err?.message ||
        `Failed to ${approved ? 'approve' : 'reject'} execution`;
      setError(errorMessage);
    } finally {
      setIsApproving(false);
    }
  };

  const formatOutput = (outputText: string): string => {
    // Try to detect if it's JSON and format it
    try {
      const parsed = JSON.parse(outputText);
      return JSON.stringify(parsed, null, 2);
    } catch {
      // Not JSON, return as-is
      return outputText;
    }
  };

  if (!isAIAssigned) {
    return null;
  }

  const getStatusColor = (currentStatus: string): string => {
    switch (currentStatus) {
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-medium text-gray-900">AI Agent Execution</h4>
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(status)}`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {status === 'pending' && (
        <div className="space-y-3">
          <p className="text-sm text-gray-600">
            This task is assigned to an AI agent. Click the button below to start execution.
          </p>
          <button
            type="button"
            onClick={handleRunAgent}
            disabled={isRunning}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? 'Starting...' : 'Run Agent'}
          </button>
        </div>
      )}

      {status === 'running' && (
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-600">AI agent is executing this task...</p>
          </div>
          <p className="text-xs text-gray-500">
            Execution status will update automatically. This may take a few moments.
          </p>
        </div>
      )}

      {(status === 'completed' || status === 'rejected') && executionOutput && (
        <div className="space-y-3">
          <div>
            <h5 className="text-sm font-medium text-gray-900 mb-2">Execution Output</h5>
            <div className="p-3 bg-white border border-gray-200 rounded-md max-h-64 overflow-y-auto">
              <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono">
                {formatOutput(executionOutput)}
              </pre>
            </div>
          </div>
        </div>
      )}

      {status === 'completed' && (
        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Approval Comment (optional)
            </label>
            <textarea
              value={approvalComment}
              onChange={(e) => setApprovalComment(e.target.value)}
              rows={2}
              placeholder="Add any comments about the execution results..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={() => handleApprovalDecision(false)}
              disabled={isApproving}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {isApproving ? 'Processing...' : 'Reject'}
            </button>
            <button
              type="button"
              onClick={() => handleApprovalDecision(true)}
              disabled={isApproving}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {isApproving ? 'Processing...' : 'Approve'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
