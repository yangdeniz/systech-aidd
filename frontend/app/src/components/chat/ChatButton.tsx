"use client";

import { cn } from "@/lib/utils";
import { MessageCircle } from "lucide-react";

interface ChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export function ChatButton({ onClick, isOpen }: ChatButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "fixed bottom-4 right-4 z-40",
        "w-14 h-14 rounded-full",
        "bg-primary text-primary-foreground",
        "shadow-lg hover:shadow-xl",
        "flex items-center justify-center",
        "transition-all duration-300",
        "hover:scale-110",
        "cursor-pointer",
        isOpen && "scale-0 opacity-0",
      )}
      aria-label="Open chat"
    >
      <MessageCircle size={24} />
    </button>
  );
}

