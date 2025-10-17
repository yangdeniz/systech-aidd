"use client";

import { ChatWindow } from "@/components/chat/ChatWindow";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function UserChatPage() {
  const { logout, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push("/login");
    }
  }, [user, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!user) {
    return null;
  }

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      {/* Header - Sticky */}
      <header className="sticky top-0 z-10 bg-background border-b">
        <div className="container mx-auto p-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">HomeGuru Chat</h1>
            <p className="text-sm text-muted-foreground">Welcome, {user.username}</p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button onClick={handleLogout} variant="outline" size="sm">
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Chat Area - Full Screen */}
      <div className="flex-1 flex overflow-hidden">
        <ChatWindow isOpen={true} onClose={() => {}} fullScreen={true} />
      </div>
    </div>
  );
}

