import React, { useState } from 'react';
import { Task } from '../types/task';
import { TaskCard } from './TaskCard';

interface SubtaskListProps {
  parentId: string;
  subtasks: Task[];
  onTaskClick?: (task: Task) => void;
  defaultExpanded?: boolean;
}

export const SubtaskList: React.FC<SubtaskListProps> = ({
  parentId,
  subtasks,
  onTaskClick,
  defaultExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!subtasks || subtasks.length === 0) {
    return null;
  }

  return (
    <div className="ml-4" role="group" aria-label="Subtasks">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 mb-2"
        aria-expanded={isExpanded}
        aria-controls={`subtasks-${parentId}`}
      >
        <span className="text-sm">{isExpanded ? '▼' : '▶'}</span>
        <span>
          {subtasks.length} subtask{subtasks.length !== 1 ? 's' : ''}
        </span>
      </button>
      {isExpanded && (
        <div
          id={`subtasks-${parentId}`}
          className="space-y-2 border-l-2 border-gray-200 pl-4"
          role="list"
          aria-label={`Subtasks of parent task ${parentId}`}
        >
          {subtasks.map((subtask) => (
            <div key={subtask.id} role="listitem">
              <TaskCard
                task={subtask}
                onClick={() => onTaskClick?.(subtask)}
                isSubtask={true}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

