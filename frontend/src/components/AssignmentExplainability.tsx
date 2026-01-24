import React from 'react';
import { AssignmentRisk } from '../types/task';

interface AssignmentExplainabilityProps {
  assignmentReason?: string;
  assignmentRisk?: AssignmentRisk;
}

export const AssignmentExplainability: React.FC<AssignmentExplainabilityProps> = ({
  assignmentReason,
  assignmentRisk,
}) => {
  if (!assignmentReason && !assignmentRisk) {
    return null;
  }

  const getRiskColor = (risk?: AssignmentRisk) => {
    switch (risk) {
      case AssignmentRisk.LOW:
        return 'bg-green-100 text-green-800 border-green-200';
      case AssignmentRisk.MEDIUM:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case AssignmentRisk.HIGH:
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Assignment Context</h3>
      <div className="space-y-3">
        {/* Assignment Reason */}
        {assignmentReason && (
          <div>
            <h4 className="text-xs font-medium text-gray-600 mb-1">Reason</h4>
            <p className="text-sm text-gray-700">{assignmentReason}</p>
          </div>
        )}

        {/* Risk Pill */}
        {assignmentRisk && (
          <div>
            <h4 className="text-xs font-medium text-gray-600 mb-1">Risk Assessment</h4>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${getRiskColor(
                assignmentRisk
              )}`}
            >
              {assignmentRisk} Risk
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
