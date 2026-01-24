import React from 'react';

const FIBONACCI_VALUES = [1, 2, 3, 5, 8, 13] as const;

interface SizePickerProps {
  value?: number;
  onChange: (size: number | undefined) => void;
  disabled?: boolean;
}

export const SizePicker: React.FC<SizePickerProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const handleClick = (size: number) => {
    if (disabled) return;
    // Toggle: if clicking the same value, clear it
    onChange(value === size ? undefined : size);
  };

  return (
    <div className="flex flex-wrap gap-2">
      {FIBONACCI_VALUES.map((size) => {
        const isSelected = value === size;
        return (
          <button
            key={size}
            type="button"
            onClick={() => handleClick(size)}
            disabled={disabled}
            className={`
              px-4 py-2 rounded-md text-sm font-medium transition-colors
              ${
                isSelected
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            `}
            aria-pressed={isSelected}
            aria-label={`Set size to ${size}`}
          >
            {size}
          </button>
        );
      })}
      {value && (
        <button
          type="button"
          onClick={() => onChange(undefined)}
          disabled={disabled}
          className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 focus:outline-none"
          aria-label="Clear size"
        >
          Clear
        </button>
      )}
    </div>
  );
};
