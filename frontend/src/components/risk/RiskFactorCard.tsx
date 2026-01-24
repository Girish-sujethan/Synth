/**
 * RiskFactorCard component for displaying individual risk factors.
 */

import { RiskFactor } from "@/types/risk";
import { Card, CardContent } from "@/components/ui/card";
import { RiskBadge } from "./RiskBadge";

interface RiskFactorCardProps {
  factor: RiskFactor;
  className?: string;
}

/**
 * Component for displaying a single risk factor with its details.
 */
export function RiskFactorCard({ factor, className }: RiskFactorCardProps) {
  return (
    <Card className={className}>
      <CardContent className="p-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-sm">{factor.factor}</h4>
            <RiskBadge riskLevel={factor.severity} size="sm" />
          </div>
          <p className="text-sm text-muted-foreground">{factor.description}</p>
        </div>
      </CardContent>
    </Card>
  );
}

