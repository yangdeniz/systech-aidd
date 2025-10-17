"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function HomePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        // Not authenticated -> redirect to login
        router.push("/login");
      } else if (user.role === "administrator") {
        // Administrator -> redirect to admin dashboard
        router.push("/admin/dashboard");
      } else {
        // Regular user -> redirect to user chat
        router.push("/user/chat");
      }
    }
  }, [user, isLoading, router]);

  // Show loading state while checking authentication
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-lg">Loading...</div>
    </div>
  );
}
