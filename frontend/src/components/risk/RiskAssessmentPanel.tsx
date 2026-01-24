/**
 * RiskAssessmentPanel component for displaying risk assessments for a task.
 */

import { useEffect } from "react";
import { RiskAssessmentResponse, AssessRisksResponse } from "@/types/risk";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useApiMutation } from "@/hooks/useApiMutation";
import { API_ENDPOINTS } from "@/config/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SubtaskAssessmentCard } from "./SubtaskAssessmentCard";
import { RiskBadge } from "./RiskBadge";
import { AlertCircle, Loader2, RefreshCw } from "lucide-react";

interface RiskAssessmentPanelProps {
  taskId: number;
  className?: string;
}

/**
 * Main panel component for displaying and managing risk assessments.
 * Handles loading states, empty states, and triggering new assessments.
 */
export function RiskAssessmentPanel({
  taskId,
  className,
}: RiskAssessmentPanelProps) {
  // Query for risk assessment
  const {
    data: assessment,
    loading,
    error,
    refetch,
    isRefetching,
  } = useApiQuery<RiskAssessmentResponse>(
    `tasks/${taskId}/risk-assessment`,
    {
      requireAuth: true,
    }
  );

  // Mutation for triggering risk assessment
  const {
    mutate: assessRisks,
    loading: assessing,
    success: assessmentTriggered,
  } = useApiMutation<AssessRisksResponse, void>(
    `tasks/${taskId}/assess-risks`,
    {
      method: "POST",
      requireAuth: true,
    }
  );

  // Refetch assessment after triggering
  useEffect(() => {
    if (assessmentTriggered) {
      // Wait a bit then refetch to see if assessment is ready
      const timer = setTimeout(() => {
        refetch();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [assessmentTriggered, refetch]);

  const handleAssessRisks = async () => {
    await assessRisks(undefined);
  };

  // Loading state
  if (loading || isRefetching) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading risk assessment...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error) {
    const isNotFound = error.status === 404;
    
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Risk Assessment</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isNotFound ? (
            <div className="text-center py-6 space-y-4">
              <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto" />
              <div>
                <p className="text-sm text-muted-foreground mb-4">
                  No risk assessment available for this task yet.
                </p>
                <Button
                  onClick={handleAssessRisks}
                  disabled={assessing}
                  className="w-full sm:w-auto"
                >
                  {assessing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Assessing Risks...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Assess Risks
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 space-y-4">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
              <div>
                <p className="text-sm text-destructive mb-2">
                  Failed to load risk assessment
                </p>
                <p className="text-xs text-muted-foreground mb-4">
                  {error.message}
                </p>
                <Button onClick={() => refetch()} variant="outline">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Retry
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // No assessment data
  if (!assessment || !assessment.assessments || assessment.assessments.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Risk Assessment</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center py-6 space-y-4">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto" />
            <div>
              <p className="text-sm text-muted-foreground mb-4">
                No risk assessments found for this task.
              </p>
              <Button
                onClick={handleAssessRisks}
                disabled={assessing}
                className="w-full sm:w-auto"
              >
                {assessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Assessing Risks...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Assess Risks
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Display assessments
  const highRiskCount = assessment.assessments.filter(
    (a) => a.risk_level === "high"
  ).length;
  const mediumRiskCount = assessment.assessments.filter(
    (a) => a.risk_level === "medium"
  ).length;
  const lowRiskCount = assessment.assessments.filter(
    (a) => a.risk_level === "low"
  ).length;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Risk Assessment</CardTitle>
          <Button
            onClick={handleAssessRisks}
            disabled={assessing}
            variant="outline"
            size="sm"
          >
            {assessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Assessing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Re-assess
              </>
            )}
          </Button>
        </div>
        <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
          <span>Created: {new Date(assessment.created_at).toLocaleDateString()}</span>
          <span>•</span>
          <span>{assessment.assessments.length} subtask{assessment.assessments.length !== 1 ? 's' : ''}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Risk Summary */}
        <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {lowRiskCount}
            </div>
            <div className="text-xs text-muted-foreground mt-1">Low Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {mediumRiskCount}
            </div>
            <div className="text-xs text-muted-foreground mt-1">Medium Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {highRiskCount}
            </div>
            <div className="text-xs text-muted-foreground mt-1">High Risk</div>
          </div>
        </div>

        {/* Assessment Cards */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold">Subtask Assessments</h3>
          {assessment.assessments.map((assessmentItem) => (
            <SubtaskAssessmentCard
              key={assessmentItem.id}
              assessment={assessmentItem}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

