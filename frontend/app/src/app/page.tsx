"use client";

import { ActivityChart } from "@/components/dashboard/ActivityChart";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RecentDialogues } from "@/components/dashboard/RecentDialogues";
import { TopUsers } from "@/components/dashboard/TopUsers";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { useStats } from "@/hooks/useStats";
import type { Period } from "@/types/api";
import { useState } from "react";

export default function HomePage() {
  const [period, setPeriod] = useState<Period>("week");
  const { data, isLoading, error } = useStats(period);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-500">
          Error loading stats. Make sure the API is running at http://localhost:8000
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto p-4 md:p-8 space-y-8">
        {/* Header with Title and Theme Toggle */}
        <header className="flex items-center justify-between">
          <h1 className="text-4xl font-bold">Dashboard</h1>
          <ThemeToggle />
        </header>

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
    </main>
  );
}
