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

// Request interceptor: Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401 errors (unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear auth and redirect to login
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

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

export async function getChatHistory(): Promise<ChatMessage[]> {
  const response = await apiClient.get<ChatMessage[]>("/api/chat/history");
  return response.data;
}

export async function clearChatHistory(): Promise<void> {
  await apiClient.post("/api/chat/clear");
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
