import React from 'react';
import { AssigneeType } from '../types/task';

interface AssigneePickerProps {
  assigneeType?: AssigneeType;
  assigneeId?: string;
  onChange: (type: AssigneeType | undefined, id?: string) => void;
  availableUsers?: Array<{ id: string; name: string }>;
  availableAgents?: Array<{ id: string; name: string }>;
  disabled?: boolean;
}

export const AssigneePicker: React.FC<AssigneePickerProps> = ({
  assigneeType,
  assigneeId,
  onChange,
  availableUsers = [],
  availableAgents = [],
  disabled = false,
}) => {
  const handleTypeChange = (type: AssigneeType | 'unassigned') => {
    if (type === 'unassigned') {
      onChange(undefined, undefined);
    } else {
      onChange(type as AssigneeType, undefined);
    }
  };

  const handleIdChange = (id: string) => {
    onChange(assigneeType, id);
  };

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Assignee Type
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleTypeChange('unassigned')}
            disabled={disabled}
            className={`
              px-4 py-2 rounded-md text-sm font-medium transition-colors
              ${
                !assigneeType || assigneeType === AssigneeType.UNASSIGNED
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              focus:outline-none focus:ring-2 focus:ring-blue-500
            `}
          >
            Unassigned
          </button>
          <button
            type="button"
            onClick={() => handleTypeChange(AssigneeType.HUMAN)}
            disabled={disabled}
            className={`
              px-4 py-2 rounded-md text-sm font-medium transition-colors
              ${
                assigneeType === AssigneeType.HUMAN
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              focus:outline-none focus:ring-2 focus:ring-blue-500
            `}
          >
            Human
          </button>
          <button
            type="button"
            onClick={() => handleTypeChange(AssigneeType.AI)}
            disabled={disabled}
            className={`
              px-4 py-2 rounded-md text-sm font-medium transition-colors
              ${
                assigneeType === AssigneeType.AI
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              focus:outline-none focus:ring-2 focus:ring-blue-500
            `}
          >
            AI Agent
          </button>
        </div>
      </div>

      {assigneeType === AssigneeType.HUMAN && availableUsers.length > 0 && (
        <div>
          <label htmlFor="user-select" className="block text-sm font-medium text-gray-700 mb-2">
            Select User
          </label>
          <select
            id="user-select"
            value={assigneeId || ''}
            onChange={(e) => handleIdChange(e.target.value)}
            disabled={disabled}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Select a user...</option>
            {availableUsers.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {assigneeType === AssigneeType.AI && availableAgents.length > 0 && (
        <div>
          <label htmlFor="agent-select" className="block text-sm font-medium text-gray-700 mb-2">
            Select AI Agent
          </label>
          <select
            id="agent-select"
            value={assigneeId || ''}
            onChange={(e) => handleIdChange(e.target.value)}
            disabled={disabled}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Select an agent...</option>
            {availableAgents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};
