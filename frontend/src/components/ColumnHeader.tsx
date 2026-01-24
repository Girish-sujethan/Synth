import React, { useState } from 'react';
import { BoardColumn } from './KanbanBoard';

interface ColumnHeaderProps {
  column: BoardColumn;
  taskCount: number;
  onSettingsClick?: () => void;
  canManage?: boolean;
}

export const ColumnHeader: React.FC<ColumnHeaderProps> = ({
  column,
  taskCount,
  onSettingsClick,
  canManage = false,
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const wipLimit = column.wip_limit;
  const isWipExceeded = wipLimit !== undefined && wipLimit !== null && taskCount > wipLimit;

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-semibold text-gray-900">{column.display_name}</h2>
        <div className="flex items-center gap-2">
          {column.is_locked && (
            <span
              className="text-xs text-gray-500"
              title="Locked column"
              aria-label="Locked column"
            >
              🔒
            </span>
          )}
          {canManage && (
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="text-gray-500 hover:text-gray-700 p-1 rounded"
                aria-label="Column settings"
                aria-expanded={showMenu}
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                  />
                </svg>
              </button>
              {showMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowMenu(false)}
                    aria-hidden="true"
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-20 border border-gray-200">
                    <button
                      onClick={() => {
                        setShowMenu(false);
                        onSettingsClick?.();
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Column Settings
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* WIP Limit Badge */}
      {wipLimit !== undefined && wipLimit !== null && (
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
              isWipExceeded
                ? 'bg-red-100 text-red-800 border border-red-300'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            {taskCount} / {wipLimit}
          </span>
          {isWipExceeded && (
            <span className="text-xs text-red-600 font-medium" role="alert">
              WIP Limit Exceeded
            </span>
          )}
        </div>
      )}
    </div>
  );
};
