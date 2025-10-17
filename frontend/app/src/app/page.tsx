"use client";

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

  return (
    <main className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">HomeGuru Dashboard</h1>
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <label htmlFor="period-select" className="font-medium">
            Period:
          </label>
          <select
            id="period-select"
            value={period}
            onChange={(e) => setPeriod(e.target.value as Period)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
          </select>
        </div>
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">API Response:</h2>
          <pre className="bg-white p-4 rounded border overflow-auto text-sm">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>
    </main>
  );
}
