import type { Period, StatsResponse } from "@/types/api";
import type {
  AuthRequest,
  AuthResponse,
  ChatMessage,
  ChatRequest,
  ChatResponse,
} from "@/types/chat";
import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Stats API
export async function getStats(period: Period): Promise<StatsResponse> {
  const response = await apiClient.get<StatsResponse>("/stats", {
    params: { period },
  });
  return response.data;
}

// Chat API
export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(
    "/api/chat/message",
    request,
  );
  return response.data;
}

export async function getChatHistory(
  sessionId: string,
): Promise<ChatMessage[]> {
  const response = await apiClient.get<ChatMessage[]>("/api/chat/history", {
    params: { session_id: sessionId },
  });
  return response.data;
}

export async function clearChatHistory(sessionId: string): Promise<void> {
  await apiClient.post("/api/chat/clear", { session_id: sessionId });
}

export async function authenticateAdmin(
  request: AuthRequest,
): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>(
    "/api/chat/auth",
    request,
  );
  return response.data;
}

export default apiClient;
