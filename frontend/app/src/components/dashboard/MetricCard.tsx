import { TrendingDown, TrendingUp } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface MetricCardProps {
  title: string;
  value: string | number;
  change_percent: number;
  description: string;
}

export function MetricCard({ title, value, change_percent, description }: MetricCardProps) {
  const isPositive = change_percent >= 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="text-xs sm:text-sm">{title}</CardDescription>
        <CardTitle className="text-3xl sm:text-4xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          {isPositive ? (
            <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-green-600 dark:text-green-400" />
          ) : (
            <TrendingDown className="h-3 w-3 sm:h-4 sm:w-4 text-red-600 dark:text-red-400" />
          )}
          <span
            className={`text-xs sm:text-sm font-medium ${
              isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            }`}
          >
            {isPositive ? "+" : ""}
            {change_percent}%
          </span>
        </div>
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{description}</p>
      </CardContent>
    </Card>
  );
}
