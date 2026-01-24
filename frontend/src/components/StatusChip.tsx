import React from 'react';

interface StatusChipProps {
  columnKey?: string;
  displayName?: string;
  className?: string;
}

export const StatusChip: React.FC<StatusChipProps> = ({
  columnKey,
  displayName,
  className = '',
}) => {
  if (!displayName && !columnKey) {
    return null;
  }

  const text = displayName || columnKey || 'Unknown';

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 ${className}`}
      title={columnKey ? `Column: ${columnKey}` : undefined}
    >
      {text}
    </span>
  );
};
