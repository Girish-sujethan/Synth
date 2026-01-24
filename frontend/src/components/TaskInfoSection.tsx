import React from 'react';
import { Task, AssignmentRisk } from '../types/task';
import { TagChips } from './TagChips';

interface TaskInfoSectionProps {
  task: Task;
}

export const TaskInfoSection: React.FC<TaskInfoSectionProps> = ({ task }) => {
  const getRiskColor = (risk?: AssignmentRisk) => {
    switch (risk) {
      case AssignmentRisk.LOW:
        return 'bg-green-100 text-green-800';
      case AssignmentRisk.MEDIUM:
        return 'bg-yellow-100 text-yellow-800';
      case AssignmentRisk.HIGH:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {/* Tags */}
      {task.tags && task.tags.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Tags</h3>
          <TagChips
            tags={task.tags}
            assigneeType={task.assignee_type}
            risk={task.assignment_risk}
          />
        </div>
      )}

      {/* Size */}
      {task.size && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Size</h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-sm font-medium bg-gray-100 text-gray-800">
            {task.size} points
          </span>
        </div>
      )}

      {/* Risk Level */}
      {task.assignment_risk && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Risk Level</h3>
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded text-sm font-medium capitalize ${getRiskColor(
              task.assignment_risk
            )}`}
          >
            {task.assignment_risk}
          </span>
        </div>
      )}

      {/* Timestamps */}
      <div className="pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 space-y-1">
          <div>
            <span className="font-medium">Created:</span>{' '}
            {new Date(task.created_at).toLocaleString()}
          </div>
          <div>
            <span className="font-medium">Updated:</span>{' '}
            {new Date(task.updated_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
};
