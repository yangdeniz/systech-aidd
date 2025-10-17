export type ChatMode = "normal" | "admin";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sql_query?: string;
  timestamp: string;
}

export interface ChatResponse {
  message: string;
  sql_query?: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  mode: ChatMode;
}

export interface AuthRequest {
  password: string;
}

export interface AuthResponse {
  token: string;
  expires_at: string;
}

