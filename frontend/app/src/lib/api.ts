import type { Period, StatsResponse } from "@/types/api";
import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function getStats(period: Period): Promise<StatsResponse> {
  const response = await apiClient.get<StatsResponse>("/stats", {
    params: { period },
  });
  return response.data;
}

export default apiClient;
