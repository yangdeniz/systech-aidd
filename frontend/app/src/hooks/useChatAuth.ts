import { authenticateAdmin } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";

const TOKEN_KEY = "chat_admin_token";
const EXPIRES_KEY = "chat_admin_token_expires";

export function useChatAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  // Check if token is valid on mount
  useEffect(() => {
    if (typeof window === "undefined") return;

    const storedToken = localStorage.getItem(TOKEN_KEY);
    const expiresAt = localStorage.getItem(EXPIRES_KEY);

    if (storedToken && expiresAt) {
      const expiryDate = new Date(expiresAt);
      if (expiryDate > new Date()) {
        setToken(storedToken);
        setIsAuthenticated(true);
      } else {
        // Token expired, clear it
        logout();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const logout = useCallback(() => {
    if (typeof window === "undefined") return;

    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXPIRES_KEY);
    setToken(null);
    setIsAuthenticated(false);
  }, []);

  const authMutation = useMutation({
    mutationFn: (password: string) => authenticateAdmin({ password }),
    onSuccess: (response) => {
      if (typeof window === "undefined") return;

      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(EXPIRES_KEY, response.expires_at);
      setToken(response.token);
      setIsAuthenticated(true);
    },
  });

  const authenticate = useCallback(
    (password: string) => {
      authMutation.mutate(password);
    },
    [authMutation],
  );

  return {
    isAuthenticated,
    token,
    authenticate,
    logout,
    isAuthenticating: authMutation.isPending,
    authError: authMutation.error,
  };
}

