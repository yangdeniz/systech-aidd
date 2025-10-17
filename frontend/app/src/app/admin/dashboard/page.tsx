"use client";

import { ActivityChart } from "@/components/dashboard/ActivityChart";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RecentDialogues } from "@/components/dashboard/RecentDialogues";
import { TopUsers } from "@/components/dashboard/TopUsers";
import { useStats } from "@/hooks/useStats";
import type { Period } from "@/types/api";
import { useState } from "react";

export default function AdminDashboardPage() {
  const [period, setPeriod] = useState<Period>("week");
  const { data, isLoading, error } = useStats(period);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-lg text-red-500">
          Error loading stats. Make sure you're authenticated and the API is running.
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="h-full overflow-auto">
      <div className="container mx-auto p-4 md:p-6 lg:p-8 space-y-6 md:space-y-8">

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.metrics.map((metric, idx) => (
            <MetricCard
              key={idx}
              title={metric.title}
              value={metric.value}
              change_percent={metric.change_percent}
              description={metric.description}
            />
          ))}
        </div>

        {/* Activity Chart */}
        <ActivityChart data={data.time_series} period={period} onPeriodChange={setPeriod} />

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <RecentDialogues dialogues={data.recent_dialogues} />
          <TopUsers users={data.top_users} />
        </div>
      </div>
    </div>
  );
}

