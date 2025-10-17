"use client";

import type { ChatMessage } from "@/types/chat";
import { Loader2 } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useRef } from "react";
import { Message } from "./Message";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  isLoadingHistory?: boolean;
}

export function MessageList({
  messages,
  isLoading,
  isLoadingHistory,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();
  
  const bgStyle = {
    backgroundColor: theme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(210 40% 96.1%)",
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center h-full" style={bgStyle}>
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground" style={bgStyle}>
        <div className="text-center">
          <p className="text-lg font-medium">Начните диалог</p>
          <p className="text-sm mt-1">
            Задайте вопрос или переключитесь в админ режим для статистики
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto px-4 py-4" style={bgStyle}>
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex justify-start mb-4">
          <div className="bg-muted rounded-lg px-4 py-2">
            <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

