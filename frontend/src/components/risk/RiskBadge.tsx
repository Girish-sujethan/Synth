/**
 * RiskBadge component for displaying risk levels with color coding.
 */

import { RiskLevel } from "@/types/risk";
import { cn } from "@/lib/utils";

interface RiskBadgeProps {
  riskLevel: RiskLevel;
  className?: string;
  size?: "sm" | "md" | "lg";
}

/**
 * Color-coded risk level badge component.
 * 
 * - Green for low risk
 * - Yellow for medium risk
 * - Red for high risk
 */
export function RiskBadge({ riskLevel, className, size = "md" }: RiskBadgeProps) {
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-1",
    lg: "text-base px-3 py-1.5",
  };

  const colorClasses = {
    low: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800",
    high: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800",
  };

  const label = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-medium",
        sizeClasses[size],
        colorClasses[riskLevel],
        className
      )}
    >
      {label} Risk
    </span>
  );
}

