/**
 * CreateTaskForm component for creating new tasks.
 */

import { useState } from "react";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Task } from "@/types/risk";
import { Loader2, Plus } from "lucide-react";

interface CreateTaskFormProps {
  onTaskCreated?: (task: Task) => void;
  onCancel?: () => void;
}

/**
 * Form component for creating a new task.
 */
export function CreateTaskForm({ onTaskCreated, onCancel }: CreateTaskFormProps) {
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("pending");

  const {
    mutate: createTask,
    loading,
    error,
    success,
  } = useApiMutation<Task, { description: string; status?: string }>(
    "tasks",
    {
      method: "POST",
      requireAuth: true,
      onSuccess: (data) => {
        if (data && onTaskCreated) {
          onTaskCreated(data);
        }
        // Reset form
        setDescription("");
        setStatus("pending");
      },
    }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) {
      return;
    }

    await createTask({
      description: description.trim(),
      status: status || "pending",
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="description" className="text-sm font-medium mb-2 block">
          Task Description
        </label>
        <Input
          id="description"
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description..."
          required
          disabled={loading}
          className="w-full"
        />
      </div>

      <div>
        <label htmlFor="status" className="text-sm font-medium mb-2 block">
          Status
        </label>
        <select
          id="status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          disabled={loading}
          className="w-full px-3 py-2 text-sm border rounded-md bg-background"
        >
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {error && (
        <div className="text-sm text-destructive">
          {error.message || "Failed to create task"}
        </div>
      )}

      {success && (
        <div className="text-sm text-green-600 dark:text-green-400">
          Task created successfully!
        </div>
      )}

      <div className="flex gap-2">
        <Button type="submit" disabled={loading || !description.trim()}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating...
            </>
          ) : (
            <>
              <Plus className="mr-2 h-4 w-4" />
              Create Task
            </>
          )}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}

