"use client";

import { ChatWindow } from "@/components/chat/ChatWindow";

export default function AdminChatPage() {
  return (
    <div className="h-full flex items-stretch p-6">
      <ChatWindow isOpen={true} onClose={() => {}} fullScreen={true} initialMode="admin" />
    </div>
  );
}

