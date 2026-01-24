import React, { useEffect, useState } from 'react';
import { BoardColumn } from './KanbanBoard';

interface ColumnSettingsModalProps {
  column: BoardColumn | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: {
    display_name?: string;
    wip_limit?: number | null;
  }) => Promise<void>;
  onDelete?: () => void;
  canDelete?: boolean;
  isLoading?: boolean;
}

export const ColumnSettingsModal: React.FC<ColumnSettingsModalProps> = ({
  column,
  isOpen,
  onClose,
  onSave,
  onDelete,
  canDelete = false,
  isLoading = false,
}) => {
  const [displayName, setDisplayName] = useState('');
  const [wipLimit, setWipLimit] = useState<string>('');

  useEffect(() => {
    if (column) {
      setDisplayName(column.display_name);
      setWipLimit(column.wip_limit?.toString() || '');
    }
  }, [column]);

  if (!isOpen || !column) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave({
      display_name: displayName.trim() || undefined,
      wip_limit: wipLimit ? parseInt(wipLimit, 10) : null,
    });
  };

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="column-settings-title"
    >
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h2 id="column-settings-title" className="text-xl font-semibold mb-4">
            Column Settings
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="display_name" className="block text-sm font-medium text-gray-700">
                Display Name
              </label>
              <input
                type="text"
                id="display_name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Column key: <code className="bg-gray-100 px-1 rounded">{column.key}</code> (cannot be changed)
              </p>
            </div>

            <div>
              <label htmlFor="wip_limit" className="block text-sm font-medium text-gray-700">
                WIP Limit (optional)
              </label>
              <input
                type="number"
                id="wip_limit"
                value={wipLimit}
                onChange={(e) => setWipLimit(e.target.value)}
                min="0"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="No limit"
              />
              <p className="mt-1 text-xs text-gray-500">
                Leave empty for no limit
              </p>
            </div>

            {column.is_locked && (
              <div className="rounded-md bg-yellow-50 p-3">
                <p className="text-sm text-yellow-800">
                  This column is locked and cannot be modified.
                </p>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4 border-t">
              {canDelete && onDelete && !column.is_locked && (
                <button
                  type="button"
                  onClick={onDelete}
                  className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500"
                  disabled={isLoading}
                >
                  Delete Column
                </button>
              )}
              <button
                type="button"
                onClick={onClose}
                className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 border border-gray-300"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
                disabled={isLoading || column.is_locked}
              >
                {isLoading ? 'Saving...' : 'Save'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
