import {
    clearChatHistory,
    getChatHistory,
    sendChatMessage,
} from "@/lib/api";
import type { ChatMessage, ChatMode } from "@/types/chat";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import { v4 as uuidv4 } from "uuid";

export function useChat() {
  // Generate or retrieve session_id from localStorage
  const sessionId = useMemo(() => {
    if (typeof window === "undefined") return "";
    let id = localStorage.getItem("chat_session_id");
    if (!id) {
      id = uuidv4();
      localStorage.setItem("chat_session_id", id);
    }
    return id;
  }, []);

  const [mode, setMode] = useState<ChatMode>("normal");
  const queryClient = useQueryClient();

  // Fetch chat history
  const {
    data: messages = [],
    isLoading: isLoadingHistory,
    error: historyError,
  } = useQuery({
    queryKey: ["chat-history", sessionId],
    queryFn: () => getChatHistory(sessionId),
    enabled: !!sessionId,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) =>
      sendChatMessage({ message, mode, session_id: sessionId }),
    onSuccess: (response) => {
      // Optimistically update the cache with new messages
      queryClient.setQueryData<ChatMessage[]>(
        ["chat-history", sessionId],
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
    mutationFn: () => clearChatHistory(sessionId),
    onSuccess: () => {
      queryClient.setQueryData<ChatMessage[]>(
        ["chat-history", sessionId],
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
    sessionId,
  };
}

