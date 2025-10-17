import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { useTheme } from "next-themes";
import { useState } from "react";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (password: string) => void;
  isAuthenticating?: boolean;
  error?: Error | null;
}

export function AuthModal({
  isOpen,
  onClose,
  onSubmit,
  isAuthenticating,
  error,
}: AuthModalProps) {
  const [password, setPassword] = useState("");
  const { theme } = useTheme();

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.trim()) {
      onSubmit(password);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div 
        className="border border-border rounded-lg shadow-lg w-full max-w-md p-6 relative"
        style={{
          backgroundColor: theme === "dark" ? "hsl(222.2 84% 4.9%)" : "white",
        }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
        >
          <X size={20} />
        </button>

        {/* Header */}
        <h2 className="text-xl font-semibold mb-2">Аутентификация</h2>
        <p className="text-sm text-muted-foreground mb-6">
          Введите пароль администратора для доступа к админ режиму
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-2"
            >
              Пароль
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={cn(
                "w-full px-3 py-2 border border-input rounded-lg",
                "bg-background text-foreground",
                "focus:outline-none focus:ring-2 focus:ring-ring",
                "disabled:opacity-50 disabled:cursor-not-allowed",
              )}
              placeholder="Введите пароль"
              disabled={isAuthenticating}
              autoFocus
            />
          </div>

          {/* Error message */}
          {error && (
            <div className="p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
              Неверный пароль. Попробуйте еще раз.
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isAuthenticating}
            >
              Отмена
            </Button>
            <Button type="submit" disabled={isAuthenticating || !password}>
              {isAuthenticating ? "Проверка..." : "Войти"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

