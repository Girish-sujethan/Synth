import React from 'react';
import { Column } from './Column';
import { Task } from '../types/task';

export interface BoardColumn {
  id: string;
  key: string;
  name: string;
  display_name: string;
  position: number;
  wip_limit?: number;
  is_locked: boolean;
  tasks?: Task[];
}

interface KanbanBoardProps {
  columns: BoardColumn[];
  onTaskClick?: (task: Task) => void;
  onColumnSettings?: (column: BoardColumn) => void;
  canManage?: boolean;
  isLoading?: boolean;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  columns,
  onTaskClick,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading board...</div>
      </div>
    );
  }

  if (!columns || columns.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-400">No columns configured</div>
      </div>
    );
  }

  // Sort columns by position
  const sortedColumns = [...columns].sort((a, b) => a.position - b.position);

  return (
    <div className="flex gap-4 overflow-x-auto pb-4" role="region" aria-label="Kanban board">
      {sortedColumns.map((column) => (
        <Column
          key={column.id}
          column={column}
          tasks={column.tasks || []}
          onTaskClick={onTaskClick}
          onColumnSettings={onColumnSettings}
          canManage={canManage}
        />
      ))}
    </div>
  );
};
