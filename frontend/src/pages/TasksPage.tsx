/**
 * TasksPage component - Task Management Dashboard with Risk Assessment.
 */

import { useState } from "react";
import { useApiQuery } from "@/hooks/useApiQuery";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RiskAssessmentPanel } from "@/components/risk/RiskAssessmentPanel";
import { CreateTaskForm } from "@/components/tasks/CreateTaskForm";
import { Task } from "@/types/risk";
import { Loader2, AlertCircle, FileText, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Task Management Dashboard page with Assignment Review Interface.
 * Displays tasks and their risk assessments for informed task assignment decisions.
 */
export function TasksPage() {
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Query for tasks list
  const {
    data: tasks,
    loading,
    error,
    refetch,
  } = useApiQuery<Task[]>("tasks", {
    requireAuth: true,
  });

  const handleTaskCreated = (task: Task) => {
    // Refresh tasks list
    refetch();
    // Select the newly created task
    setSelectedTaskId(task.id);
    setShowCreateForm(false);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Task Management Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Review tasks and their risk assessments for informed assignment decisions
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tasks List Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Tasks</CardTitle>
                <Button
                  onClick={() => setShowCreateForm(!showCreateForm)}
                  size="sm"
                  variant="outline"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New Task
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {showCreateForm && (
                <div className="mb-6 pb-6 border-b">
                  <CreateTaskForm
                    onTaskCreated={handleTaskCreated}
                    onCancel={() => setShowCreateForm(false)}
                  />
                </div>
              )}
              {loading ? (
                <div className="flex items-center justify-center py-8 text-muted-foreground">
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  <span>Loading tasks...</span>
                </div>
              ) : error ? (
                <div className="text-center py-8 space-y-4">
                  <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto" />
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">
                      Tasks endpoint not available yet
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Enter a task ID below to view risk assessments
                    </p>
                  </div>
                </div>
              ) : tasks && tasks.length > 0 ? (
                <div className="space-y-2">
                  {tasks.map((task) => (
                    <button
                      key={task.id}
                      onClick={() => setSelectedTaskId(task.id)}
                      className={cn(
                        "w-full text-left p-3 rounded-md border transition-colors",
                        selectedTaskId === task.id
                          ? "bg-primary text-primary-foreground border-primary"
                          : "hover:bg-accent border-border"
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">
                            {task.description}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            ID: {task.id} • {task.status || "pending"}
                          </p>
                        </div>
                        <FileText className="h-4 w-4 ml-2 flex-shrink-0" />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 space-y-4">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto" />
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">
                      No tasks available
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Create a new task to get started
                    </p>
                  </div>
                </div>
              )}

              {/* Manual Task ID Input (fallback) */}
              {tasks && tasks.length === 0 && (
                <div className="mt-6 pt-6 border-t">
                  <label className="text-sm font-medium mb-2 block">
                    Or view by Task ID
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="Enter task ID"
                      value={selectedTaskId || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setSelectedTaskId(value ? parseInt(value, 10) : null);
                      }}
                      className="flex-1 px-3 py-2 text-sm border rounded-md bg-background"
                      min="1"
                    />
                    <Button
                      onClick={() => refetch()}
                      variant="outline"
                      size="sm"
                      disabled={!selectedTaskId}
                    >
                      Load
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Risk Assessment Panel */}
        <div className="lg:col-span-2">
          {selectedTaskId ? (
            <RiskAssessmentPanel taskId={selectedTaskId} />
          ) : (
            <Card>
              <CardContent className="p-12">
                <div className="text-center space-y-4">
                  <FileText className="h-16 w-16 text-muted-foreground mx-auto" />
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Select a Task
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Choose a task from the list or enter a task ID to view its risk assessment
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

