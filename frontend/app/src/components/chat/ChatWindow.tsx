"use client";

import {
  ChatInput,
  ChatInputSubmit,
  ChatInputTextArea,
} from "@/components/ui/chat-input";
import { useChat } from "@/hooks/useChat";
import { useChatAuth } from "@/hooks/useChatAuth";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { AuthModal } from "./AuthModal";
import { MessageList } from "./MessageList";
import { ModeToggle } from "./ModeToggle";

interface ChatWindowProps {
  isOpen: boolean;
  onClose: () => void;
  fullScreen?: boolean;
  initialMode?: "normal" | "admin";
}

export function ChatWindow({ isOpen, onClose, fullScreen = false, initialMode = "normal" }: ChatWindowProps) {
  const [message, setMessage] = useState("");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { theme } = useTheme();

  const {
    messages,
    mode,
    setMode,
    sendMessage,
    isLoading,
    isLoadingHistory,
  } = useChat();

  // Set initial mode on mount
  useEffect(() => {
    if (initialMode && mode !== initialMode) {
      setMode(initialMode);
    }
  }, [initialMode, setMode, mode]);

  const { isAuthenticated, authenticate, isAuthenticating, authError } =
    useChatAuth();

  const handleSendMessage = () => {
    if (message.trim()) {
      sendMessage(message);
      setMessage("");
    }
  };

  const handleModeChange = (newMode: "normal" | "admin") => {
    setMode(newMode);
  };

  const handleAuthSubmit = (password: string) => {
    authenticate(password);
    // Close modal on successful auth (will be handled by useEffect in useChatAuth)
  };

  // Auto-switch to admin mode after successful auth
  useState(() => {
    if (isAuthenticated && showAuthModal) {
      setMode("admin");
      setShowAuthModal(false);
    }
  });

  if (!isOpen) return null;

  return (
    <>
      {/* Chat Window */}
      <div
        className={cn(
          "flex flex-col",
          fullScreen
            ? "w-full h-full max-w-4xl mx-auto bg-background"
            : "fixed bottom-20 right-4 z-50 w-[400px] h-[600px] md:w-[400px] md:h-[600px] max-md:w-[calc(100vw-2rem)] max-md:h-[calc(100vh-8rem)] border border-border rounded-lg shadow-2xl animate-in slide-in-from-bottom-4 duration-300",
        )}
        style={
          fullScreen
            ? undefined
            : {
                backgroundColor:
                  theme === "dark" ? "hsl(222.2 84% 4.9%)" : "white",
              }
        }
      >
        {/* Header - only for floating mode */}
        {!fullScreen && (
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center gap-3">
              <h3 className="font-semibold">Chat</h3>
              <ModeToggle
                mode={mode}
                onModeChange={handleModeChange}
                isAuthenticated={isAuthenticated}
                onAuthRequired={() => setShowAuthModal(true)}
              />
            </div>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
            >
              <X size={20} />
            </button>
          </div>
        )}

        {/* Messages - Scrollable area */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            isLoadingHistory={isLoadingHistory}
          />
        </div>

        {/* Input - Fixed at bottom */}
        <div className={cn(
          "p-4 border-t border-border flex-shrink-0",
          fullScreen && "bg-background"
        )}>
          <ChatInput
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onSubmit={handleSendMessage}
            loading={isLoading}
            variant="default"
          >
            <ChatInputTextArea
              placeholder={
                mode === "admin"
                  ? "Задайте вопрос о статистике..."
                  : "Напишите сообщение..."
              }
            />
            <ChatInputSubmit />
          </ChatInput>
        </div>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSubmit={handleAuthSubmit}
        isAuthenticating={isAuthenticating}
        error={authError}
      />
    </>
  );
}

