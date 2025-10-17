import {
  clearChatHistory,
  getChatHistory,
  sendChatMessage,
} from "@/lib/api";
import type { ChatMessage, ChatMode } from "@/types/chat";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";

export function useChat() {
  const [mode, setMode] = useState<ChatMode>("normal");
  const queryClient = useQueryClient();

  // Get current user_id from localStorage for cache key isolation
  const userId = useMemo(() => {
    if (typeof window === "undefined") return null;
    const userStr = localStorage.getItem("auth_user");
    if (!userStr) return null;
    try {
      const user = JSON.parse(userStr);
      return user.user_id;
    } catch {
      return null;
    }
  }, []);

  // Fetch chat history (используется JWT токен из localStorage)
  const {
    data: messages = [],
    isLoading: isLoadingHistory,
    error: historyError,
  } = useQuery({
    queryKey: ["chat-history", userId],
    queryFn: () => getChatHistory(),
    enabled: typeof window !== "undefined" && !!localStorage.getItem("auth_token") && !!userId,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) =>
      sendChatMessage({ message, mode }),
    onSuccess: (response) => {
      // Optimistically update the cache with new messages
      queryClient.setQueryData<ChatMessage[]>(
        ["chat-history", userId],
        (old = []) => [
          ...old,
          {
            role: "user" as const,
            content: sendMessageMutation.variables || "",
            timestamp: new Date().toISOString(),
          },
          {
            role: "assistant" as const,
            content: response.message,
            sql_query: response.sql_query,
            timestamp: response.timestamp,
          },
        ],
      );
    },
  });

  // Clear history mutation
  const clearHistoryMutation = useMutation({
    mutationFn: () => clearChatHistory(),
    onSuccess: () => {
      queryClient.setQueryData<ChatMessage[]>(
        ["chat-history", userId],
        [],
      );
    },
  });

  const sendMessage = useCallback(
    (message: string) => {
      if (message.trim()) {
        sendMessageMutation.mutate(message);
      }
    },
    [sendMessageMutation],
  );

  const clearHistory = useCallback(() => {
    clearHistoryMutation.mutate();
  }, [clearHistoryMutation]);

  return {
    messages,
    mode,
    setMode,
    sendMessage,
    clearHistory,
    isLoading: sendMessageMutation.isPending,
    isLoadingHistory,
    error: sendMessageMutation.error || historyError,
  };
}

