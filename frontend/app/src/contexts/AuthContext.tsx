"use client";

import { useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

interface User {
  user_id: number;
  username: string;
  role: string;
  token: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, firstName?: string) => Promise<void>;
  logout: () => void;
  verifyAndRestoreSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_TOKEN_KEY = "auth_token";
const AUTH_USER_KEY = "auth_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  const verifyAndRestoreSession = useCallback(async () => {
    if (typeof window === "undefined") return;

    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const userStr = localStorage.getItem(AUTH_USER_KEY);

    if (!token || !userStr) {
      setIsLoading(false);
      return;
    }

    try {
      // Verify token with backend
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/verify?token=${encodeURIComponent(token)}`
      );

      if (response.ok) {
        const data = await response.json();
        if (data.valid) {
          const userData = JSON.parse(userStr);
          setUser(userData);
        } else {
          // Token invalid, clear storage
          localStorage.removeItem(AUTH_TOKEN_KEY);
          localStorage.removeItem(AUTH_USER_KEY);
        }
      } else {
        // Server error, clear storage
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(AUTH_USER_KEY);
      }
    } catch (error) {
      console.error("Error verifying session:", error);
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(AUTH_USER_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    verifyAndRestoreSession();
  }, [verifyAndRestoreSession]);

  const login = useCallback(async (username: string, password: string) => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/login`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }

    const data = await response.json();
    const userData: User = {
      user_id: data.user_id,
      username: data.username,
      role: data.role,
      token: data.token,
    };

    localStorage.setItem(AUTH_TOKEN_KEY, data.token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));
    setUser(userData);
  }, []);

  const register = useCallback(
    async (username: string, password: string, firstName?: string) => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, first_name: firstName }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Registration failed");
      }

      const data = await response.json();
      const userData: User = {
        user_id: data.user_id,
        username: data.username,
        role: data.role,
        token: data.token,
      };

      localStorage.setItem(AUTH_TOKEN_KEY, data.token);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));
      setUser(userData);
    },
    []
  );

  const logout = useCallback(() => {
    if (typeof window === "undefined") return;

    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    // Clean up old session_id (no longer used)
    localStorage.removeItem("chat_session_id");
    setUser(null);

    // Clear all React Query cache to prevent showing data from previous user
    queryClient.clear();

    // Optional: Call backend logout endpoint
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/logout`, {
      method: "POST",
    }).catch(() => {
      // Ignore errors
    });
  }, [queryClient]);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, register, logout, verifyAndRestoreSession }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

