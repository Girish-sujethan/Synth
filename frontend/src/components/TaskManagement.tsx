import React, { useState } from 'react';
import { Task } from '../types/task';
import { KanbanBoard, BoardColumn } from './KanbanBoard';
import { TaskDrawer } from './TaskDrawer';
import { TaskForm } from './TaskForm';
import { DeleteTaskDialog } from './DeleteTaskDialog';
import { ColumnSettingsModal } from './ColumnSettingsModal';
import {
  useTasks,
  useTask,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
} from '../hooks/useTasks';
import {
  useColumns,
  useUpdateColumn,
  useDeleteColumn,
  useMoveTask,
} from '../hooks/useColumns';
import { TaskCreateRequest, TaskUpdateRequest } from '../types/task';

interface TaskManagementProps {
  teamId: string;
  userRole?: 'admin' | 'manager' | 'member' | 'viewer';
}

export const TaskManagement: React.FC<TaskManagementProps> = ({
  teamId,
  userRole = 'member',
}) => {
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isFormOpen, setFormOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);

  const { data: boardData, isLoading, error } = useTasks(teamId);
  
  // Fetch full task details when drawer opens
  const {
    data: selectedTask,
    isLoading: isTaskLoading,
    error: taskError,
  } = useTask(selectedTaskId || '', teamId);

  const createTaskMutation = useCreateTask(teamId);
  const updateTaskMutation = useUpdateTask(teamId);
  const deleteTaskMutation = useDeleteTask(teamId);
  const moveTaskMutation = useMoveTask(teamId);

  const canEdit = ['admin', 'manager', 'member'].includes(userRole);
  const canDelete = ['admin', 'manager'].includes(userRole);
  const canManageColumns = userRole === 'admin';

  const handleTaskClick = (task: Task) => {
    // Set task ID to trigger useTask hook
    setSelectedTaskId(task.id);
    setIsDrawerOpen(true);
  };

  const handleCreateTask = () => {
    setSelectedTask(null);
    setIsEditMode(false);
    setFormOpen(true);
  };

  const handleEditTask = () => {
    setIsEditMode(true);
    setIsDrawerOpen(false);
    setFormOpen(true);
  };

  const handleDeleteTask = () => {
    setTaskToDelete(selectedTask);
    setIsDrawerOpen(false);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data: TaskCreateRequest | TaskUpdateRequest) => {
    try {
      if (isEditMode && selectedTask) {
        await updateTaskMutation.mutateAsync({
          taskId: selectedTask.id,
          data: data as TaskUpdateRequest,
        });
        setFormOpen(false);
        setSelectedTask(null);
        setIsEditMode(false);
      } else if (selectedTask) {
        // Inline edit from drawer
        await updateTaskMutation.mutateAsync({
          taskId: selectedTask.id,
          data: data as TaskUpdateRequest,
        });
        // Don't close drawer, just update the task
      } else {
        await createTaskMutation.mutateAsync(data as TaskCreateRequest);
        setFormOpen(false);
        setSelectedTask(null);
        setIsEditMode(false);
      }
    } catch (error) {
      // Error handling is done by the mutation
      console.error('Task operation failed:', error);
      throw error; // Re-throw for inline editing
    }
  };

  const handleDeleteConfirm = async () => {
    if (!taskToDelete) return;

    try {
      await deleteTaskMutation.mutateAsync(taskToDelete.id);
      setIsDeleteDialogOpen(false);
      setTaskToDelete(null);
      setSelectedTask(null);
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading tasks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-red-600">
          Error loading tasks. Please try again.
        </div>
      </div>
    );
  }

  const columns: BoardColumn[] = (boardData?.columns || []).map((col: any) => ({
    id: col.id,
    key: col.key || col.name,
    name: col.name,
    display_name: col.display_name || col.name,
    position: col.position,
    wip_limit: col.wip_limit,
    is_locked: col.is_locked || false,
    tasks: col.tasks || [],
  }));

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Task Board</h1>
        {canEdit && (
          <button
            onClick={handleCreateTask}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            + Create Task
          </button>
        )}
      </div>

      {/* Kanban Board */}
      <KanbanBoard
        columns={columns}
        onTaskClick={handleTaskClick}
        onColumnSettings={canManageColumns ? handleColumnSettings : undefined}
        canManage={canManageColumns}
        isLoading={isLoading}
      />

      {/* Task Drawer */}
      <TaskDrawer
        task={selectedTask || null}
        isOpen={isDrawerOpen}
        isLoading={isTaskLoading}
        error={taskError ? 'Failed to load task details' : null}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedTaskId(null);
        }}
        onEdit={handleEditTask}
        onDelete={handleDeleteTask}
        onParentClick={handleParentClick}
        canEdit={canEdit}
        teamId={teamId}
        onRefresh={() => {
          // Refresh task data
          if (selectedTaskId) {
            setSelectedTaskId(null);
            setTimeout(() => setSelectedTaskId(selectedTaskId), 100);
          }
        }}
        canDelete={canDelete}
        columns={columns}
      />

      {/* Task Form Modal */}
      {isFormOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
            <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
              <h2 className="text-xl font-semibold mb-4">
                {isEditMode ? 'Edit Task' : 'Create Task'}
              </h2>
              <TaskForm
                task={isEditMode ? selectedTask : undefined}
                onSubmit={handleFormSubmit}
                onCancel={() => {
                  setFormOpen(false);
                  setSelectedTask(null);
                  setIsEditMode(false);
                }}
                isLoading={
                  createTaskMutation.isPending || updateTaskMutation.isPending
                }
                error={
                  (createTaskMutation.error as any)?.response?.data?.error?.message ||
                  (updateTaskMutation.error as any)?.response?.data?.error?.message ||
                  (createTaskMutation.error as any)?.message ||
                  (updateTaskMutation.error as any)?.message ||
                  null
                }
                availableColumns={columns.map((col: any) => ({
                  id: col.id,
                  key: col.key || col.name,
                  name: col.display_name || col.name,
                }))}
              />
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <DeleteTaskDialog
        isOpen={isDeleteDialogOpen}
        taskTitle={taskToDelete?.title || ''}
        subtaskCount={taskToDelete?.subtask_count || 0}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setIsDeleteDialogOpen(false);
          setTaskToDelete(null);
        }}
        isLoading={deleteTaskMutation.isPending}
      />

      {/* Column Settings Modal */}
      <ColumnSettingsModal
        column={selectedColumn}
        isOpen={isColumnSettingsOpen}
        onClose={() => {
          setIsColumnSettingsOpen(false);
          setSelectedColumn(null);
        }}
        onSave={handleColumnSave}
        onDelete={handleColumnDelete}
        canDelete={canManageColumns}
        isLoading={updateColumnMutation.isPending || deleteColumnMutation.isPending}
      />
    </div>
  );
};
