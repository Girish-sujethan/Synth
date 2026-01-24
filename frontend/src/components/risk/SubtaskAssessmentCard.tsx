/**
 * SubtaskAssessmentCard component for displaying risk assessment for a subtask.
 */

import { useState } from "react";
import { AssessmentItem } from "@/types/risk";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RiskBadge } from "./RiskBadge";
import { RiskFactorCard } from "./RiskFactorCard";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";

interface SubtaskAssessmentCardProps {
  assessment: AssessmentItem;
  className?: string;
}

/**
 * Expandable card component for displaying subtask risk assessment.
 * Highlights high-risk subtasks and shows detailed risk factors and mitigation suggestions.
 */
export function SubtaskAssessmentCard({
  assessment,
  className,
}: SubtaskAssessmentCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isHighRisk = assessment.risk_level === "high";
  const hasRiskFactors = assessment.risk_factors && assessment.risk_factors.length > 0;

  return (
    <Card
      className={cn(
        "transition-all",
        isHighRisk && "border-red-300 dark:border-red-700 bg-red-50/50 dark:bg-red-950/20",
        className
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isHighRisk && (
              <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
            )}
            <div>
              <CardTitle className="text-base">
                {assessment.subtask_id || "Task Assessment"}
              </CardTitle>
              {assessment.subtask_id && (
                <p className="text-xs text-muted-foreground mt-1">
                  Subtask ID: {assessment.subtask_id}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <RiskBadge riskLevel={assessment.risk_level} />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-8 w-8"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0 space-y-4">
          {/* Risk Factors */}
          {hasRiskFactors ? (
            <div>
              <h4 className="text-sm font-semibold mb-3">
                Risk Factors ({assessment.risk_factors!.length})
              </h4>
              <div className="space-y-2">
                {assessment.risk_factors!.map((factor, index) => (
                  <RiskFactorCard key={index} factor={factor} />
                ))}
              </div>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              No specific risk factors identified.
            </div>
          )}

          {/* Mitigation Suggestions */}
          {assessment.mitigation_suggestions && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Mitigation Suggestions</h4>
              <div className="p-3 bg-muted rounded-md">
                <p className="text-sm text-muted-foreground">
                  {assessment.mitigation_suggestions}
                </p>
              </div>
            </div>
          )}

          {!hasRiskFactors && !assessment.mitigation_suggestions && (
            <div className="text-sm text-muted-foreground text-center py-4">
              No additional details available for this assessment.
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}

