import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/types/chat";
import { ChevronDown, ChevronUp, Code } from "lucide-react";
import { useState } from "react";

interface MessageProps {
  message: ChatMessage;
}

export function Message({ message }: MessageProps) {
  const [sqlExpanded, setSqlExpanded] = useState(false);
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3 shadow-sm",
          isUser
            ? "bg-primary/95 text-primary-foreground backdrop-blur-sm"
            : "bg-muted/80 text-foreground backdrop-blur-sm border border-border/50",
        )}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>

        {/* SQL query для admin режима */}
        {message.sql_query && (
          <div className="mt-3 border-t border-border/50 pt-3">
            <button
              onClick={() => setSqlExpanded(!sqlExpanded)}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
            >
              <Code size={16} />
              <span>SQL Query</span>
              {sqlExpanded ? (
                <ChevronUp size={16} />
              ) : (
                <ChevronDown size={16} />
              )}
            </button>

            {sqlExpanded && (
              <pre className="mt-2 p-3 rounded-lg text-xs overflow-x-auto bg-background/50 border border-border/30 backdrop-blur-sm">
                <code>{message.sql_query}</code>
              </pre>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-2 text-xs opacity-70">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

