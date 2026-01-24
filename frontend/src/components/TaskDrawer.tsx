import React, { useEffect, useRef, useState } from 'react';
import { Task, AssigneeType, AssignmentRisk } from '../types/task';
import { TagChips } from './TagChips';
import { TaskMoveControl } from './TaskMoveControl';
import { TaskInfoDisplay } from './TaskInfoDisplay';
import { TaskMetaHeader } from './TaskMetaHeader';
import { TaskInfoSection } from './TaskInfoSection';
import { HierarchySection } from './HierarchySection';
import { AssignmentExplainability } from './AssignmentExplainability';
import { BoardColumn } from './KanbanBoard';
import { TaskUpdateRequest } from '../types/task';
import { SplitTaskModal } from './SplitTaskModal';
import { OrchestrationPreviewModal } from './OrchestrationPreviewModal';
import { AIExecutionPanel } from './AIExecutionPanel';

interface TaskDrawerProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: () => void;
  onDelete: () => void;
  onMove?: (columnKey: string) => Promise<void>;
  onSave?: (data: TaskUpdateRequest) => Promise<void>;
  onParentClick?: (parentId: string) => void;
  columns?: BoardColumn[];
  canEdit: boolean;
  canDelete: boolean;
  isMoving?: boolean;
  isSaving?: boolean;
  isLoading?: boolean;
  error?: string | null;
  saveError?: string | null;
  availableColumns?: Array<{ id: string; key: string; name: string }>;
  parentTitle?: string;
  auditHistory?: Array<{
    id: string;
    event_type: string;
    created_at: string;
    user_id?: string;
    payload: Record<string, any>;
  }>;
  teamId: string;
  teamMembers?: Array<{ user_id: string; name: string; level?: string }>;
  aiAgents?: Array<{ id: string; name: string }>;
  onRefresh?: () => void;
}

export const TaskDrawer: React.FC<TaskDrawerProps> = ({
  task,
  isOpen,
  onClose,
  onEdit,
  onDelete,
  onMove,
  onSave,
  onParentClick,
  columns = [],
  canEdit,
  canDelete,
  isMoving = false,
  isSaving = false,
  isLoading = false,
  error = null,
  saveError = null,
  availableColumns = [],
  parentTitle,
  auditHistory,
  teamId,
  teamMembers = [],
  aiAgents = [],
  onRefresh,
}) => {
  const drawerRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const [isSplitModalOpen, setIsSplitModalOpen] = useState(false);
  const [isOrchestrationModalOpen, setIsOrchestrationModalOpen] = useState(false);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    // Store the previously focused element
    previousActiveElement.current = document.activeElement as HTMLElement;

    // Focus the close button when drawer opens
    if (closeButtonRef.current) {
      closeButtonRef.current.focus();
    }

    // Handle Escape key
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

      // Trap focus within drawer
      const handleTab = (e: KeyboardEvent) => {
        if (!drawerRef.current) return;

        const focusableElements = drawerRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('keydown', handleTab);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTab);
      // Restore focus to previous element when drawer closes
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Loading state
  if (isLoading) {
    return (
      <div
        className="fixed inset-0 z-50 overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-drawer-title"
      >
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
        <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div className="w-screen max-w-2xl">
            <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading task details...</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !task) {
    return (
      <div
        className="fixed inset-0 z-50 overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-drawer-title"
      >
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
        <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div className="w-screen max-w-2xl">
            <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
              <div className="flex items-center justify-center h-full">
                <div className="text-center px-6">
                  <div className="text-red-600 text-4xl mb-4">⚠</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Task</h3>
                  <p className="text-gray-600 mb-4">{error}</p>
                  <button
                    onClick={onClose}
                    className="rounded-md bg-gray-600 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-500"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!task) return null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-hidden"
      role="dialog"
      aria-modal="true"
      aria-labelledby="task-drawer-title"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-2xl">
          <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
            {/* Header */}
            <div className="sticky top-0 bg-white px-4 py-6 sm:px-6 border-b z-10">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <TaskMetaHeader task={task} columns={columns} />
                </div>
                <div className="flex items-center gap-2 ml-4">
                  {canEdit && onEdit && !onSave && (
                    <button
                      onClick={onEdit}
                      className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                    >
                      Edit
                    </button>
                  )}
                  {task && !task.parent_id && task.subtask_count === 0 && (
                    <button
                      onClick={() => setIsSplitModalOpen(true)}
                      className="rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600"
                    >
                      Split Task
                    </button>
                  )}
                  {task && !task.parent_id && task.subtask_count > 0 && (
                    <button
                      onClick={() => setIsOrchestrationModalOpen(true)}
                      className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    >
                      Orchestrate
                    </button>
                  )}
                  {canDelete && (
                    <button
                      onClick={onDelete}
                      className="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                    >
                      Delete
                    </button>
                  )}
                  <button
                    ref={closeButtonRef}
                    onClick={onClose}
                    className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600"
                    aria-label="Close drawer"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 px-4 py-6 sm:px-6 overflow-y-auto">
              {/* Read-first mode: Display information */}
              {!onSave ? (
                <div className="space-y-6">
                  {/* Description */}
                  {task.description && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
                      <p className="text-gray-700 whitespace-pre-wrap text-sm">
                        {task.description}
                      </p>
                    </div>
                  )}

                  {/* Task Info Section */}
                  <TaskInfoSection task={task} />

                  {/* Hierarchy Section */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Hierarchy</h3>
                    <HierarchySection
                      task={task}
                      parentTitle={task.parent_title || parentTitle}
                      subtasksPreview={task.subtasks_preview}
                      onParentClick={onParentClick}
                    />
                  </div>

                  {/* Assignment Explainability */}
                  {(task.assignment_reason || task.assignment_risk) && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-3">Assignment Context</h3>
                      <AssignmentExplainability
                        assignmentReason={task.assignment_reason}
                        assignmentRisk={task.assignment_risk}
                      />
                    </div>
                  )}

                  {/* Task Movement */}
                  {onMove && columns.length > 0 && (
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-3">
                        Move Task
                      </h3>
                      <TaskMoveControl
                        currentColumnKey={task.column_key}
                        columns={columns}
                        onMove={onMove}
                        isLoading={isMoving}
                        showQuickActions={true}
                        taskAssigneeType={task.assignee_type}
                        taskTags={task.tags || []}
                      />
                    </div>
                  )}
                </div>
              ) : (
                /* Edit mode: Use TaskInfoDisplay */
                <TaskInfoDisplay
                  task={task}
                  canEdit={canEdit}
                  onSave={onSave}
                  isLoading={isSaving}
                  error={saveError}
                  availableColumns={availableColumns}
                />
              )}

              {/* Section 2: Audit Trail */}
              <section className="mb-8 border-t pt-6" aria-labelledby="audit-heading">
                <h2 id="audit-heading" className="text-xl font-semibold text-gray-900 mb-4">
                  Audit Trail
                </h2>
                {auditHistory && auditHistory.length > 0 ? (
                  <div className="space-y-3">
                    {auditHistory.map((event) => (
                      <div
                        key={event.id}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900 capitalize">
                            {event.event_type.replace(/_/g, ' ')}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(event.created_at).toLocaleString()}
                          </span>
                        </div>
                        {event.user_id && (
                          <div className="text-xs text-gray-600 mb-1">
                            By: {event.user_id.slice(0, 8)}...
                          </div>
                        )}
                        {Object.keys(event.payload).length > 0 && (
                          <details className="mt-2">
                            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                              View details
                            </summary>
                            <pre className="mt-2 text-xs bg-white p-2 rounded border overflow-x-auto">
                              {JSON.stringify(event.payload, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No audit history available.</p>
                )}
              </section>

              {/* Section 3: AI Execution */}
              <section className="mb-8 border-t pt-6" aria-labelledby="ai-execution-heading">
                <h2 id="ai-execution-heading" className="text-xl font-semibold text-gray-900 mb-4">
                  AI Execution
                </h2>
                {task.assignee_type === AssigneeType.AI ? (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <p className="text-sm text-blue-900 mb-2">
                      This task is assigned to an AI agent.
                    </p>
                    <p className="text-xs text-blue-700">
                      AI execution panel will appear here when the agent starts working on this task.
                    </p>
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
                    This task is not assigned to an AI agent.
                  </div>
                )}
              </section>

              {/* Metadata */}
              <div className="border-t pt-6 text-xs text-gray-500">
                <div>Created: {new Date(task.created_at).toLocaleString()}</div>
                <div>Updated: {new Date(task.updated_at).toLocaleString()}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Split Task Modal */}
      {task && (
        <SplitTaskModal
          taskId={task.id}
          teamId={teamId}
          isOpen={isSplitModalOpen}
          onClose={() => setIsSplitModalOpen(false)}
          onSuccess={() => {
            if (onRefresh) onRefresh();
            setIsSplitModalOpen(false);
          }}
        />
      )}

      {/* Orchestration Preview Modal */}
      {task && task.subtasks_preview && (
        <OrchestrationPreviewModal
          taskId={task.id}
          teamId={teamId}
          isOpen={isOrchestrationModalOpen}
          onClose={() => setIsOrchestrationModalOpen(false)}
          onSuccess={() => {
            if (onRefresh) onRefresh();
            setIsOrchestrationModalOpen(false);
          }}
          subtasks={task.subtasks_preview.map((st) => ({
            id: st.id,
            title: st.title,
            tags: task.tags || [],
          }))}
          teamMembers={teamMembers}
          aiAgents={aiAgents}
        />
      )}
    </div>
  );
};
