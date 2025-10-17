import { cn } from "@/lib/utils";
import type { ChatMode } from "@/types/chat";
import { MessageSquare, Shield } from "lucide-react";

interface ModeToggleProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  isAuthenticated: boolean;
  onAuthRequired: () => void;
}

export function ModeToggle({
  mode,
  onModeChange,
  isAuthenticated,
  onAuthRequired,
}: ModeToggleProps) {
  const handleToggle = () => {
    if (mode === "normal") {
      // Switching to admin mode
      if (!isAuthenticated) {
        onAuthRequired();
      } else {
        onModeChange("admin");
      }
    } else {
      // Switching back to normal
      onModeChange("normal");
    }
  };

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-full">
      <button
        onClick={handleToggle}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1 rounded-full transition-all text-sm font-medium cursor-pointer",
          mode === "normal"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground",
        )}
      >
        <MessageSquare size={14} />
        <span>Normal</span>
      </button>

      <button
        onClick={handleToggle}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1 rounded-full transition-all text-sm font-medium cursor-pointer",
          mode === "admin"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground",
        )}
      >
        <Shield size={14} />
        <span>Admin</span>
      </button>
    </div>
  );
}

