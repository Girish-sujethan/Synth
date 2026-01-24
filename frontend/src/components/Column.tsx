import React from 'react';
import { Task } from '../types/task';
import { TaskCard } from './TaskCard';
import { SubtaskList } from './SubtaskList';
import { ColumnHeader } from './ColumnHeader';
import { BoardColumn } from './KanbanBoard';

interface ColumnProps {
  column: BoardColumn;
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onColumnSettings?: (column: BoardColumn) => void;
  canManage?: boolean;
}

export const Column: React.FC<ColumnProps> = ({ column, tasks, onTaskClick, onColumnSettings, canManage }) => {
  // Separate parent tasks and subtasks
  // Group tasks by parent_id from API response (flat array)
  const parentTasks = tasks.filter((task) => !task.parent_id);
  const subtasksByParent = tasks
    .filter((task) => task.parent_id)
    .reduce((acc, task) => {
      const parentId = task.parent_id!;
      if (!acc[parentId]) {
        acc[parentId] = [];
      }
      acc[parentId].push(task);
      return acc;
    }, {} as Record<string, Task[]>);
  
  // Note: Subtasks can be in different columns from their parent
  // We show subtasks under their parent if parent is in this column
  // Subtasks in other columns are shown in their respective columns

  // Count only parent tasks for WIP (subtasks are counted separately)
  const wipCount = parentTasks.length;

  return (
    <div
      className="flex-shrink-0 w-80 bg-gray-50 rounded-lg p-4"
      role="region"
      aria-label={`Column: ${column.display_name}`}
    >
      {/* Column Header */}
      <ColumnHeader
        column={column}
        taskCount={wipCount}
        onSettingsClick={() => onColumnSettings?.(column)}
        canManage={canManage}
      />

      {/* Tasks */}
      <div className="space-y-3 min-h-[200px]">
        {parentTasks.length === 0 && tasks.filter((t) => t.parent_id).length === 0 ? (
          <div className="text-sm text-gray-400 text-center py-8">No tasks</div>
        ) : (
          <>
            {/* Parent tasks with their subtasks (if subtasks are in same column) */}
            {parentTasks.map((task) => {
              const subtasksInColumn = subtasksByParent[task.id] || [];
              return (
                <div key={task.id} className="space-y-2">
                  <TaskCard task={task} onClick={() => onTaskClick?.(task)} />
                  {subtasksInColumn.length > 0 && (
                    <SubtaskList
                      parentId={task.id}
                      subtasks={subtasksInColumn}
                      onTaskClick={onTaskClick}
                    />
                  )}
                </div>
              );
            })}
            
            {/* Standalone subtasks that are in this column but parent is in different column */}
            {tasks
              .filter((task) => {
                // Show subtask if it's in this column but parent is not
                if (!task.parent_id) return false;
                const parentTask = parentTasks.find((p) => p.id === task.parent_id);
                return !parentTask; // Parent is not in this column
              })
              .map((task) => (
                <div key={task.id} className="space-y-2">
                  <TaskCard task={task} onClick={() => onTaskClick?.(task)} isSubtask={true} />
                </div>
              ))}
          </>
        )}
      </div>
    </div>
  );
};
