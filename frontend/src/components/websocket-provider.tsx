"use client";

/**
 * WebSocketProvider
 *
 * A thin client component that activates the WebSocket notifications hook
 * for the authenticated user. Placed inside the dashboard layout so it runs
 * for every page under /dashboard without polluting individual pages.
 */

import { useAuth } from "@/lib/auth-context";
import { useWebSocketNotifications } from "@/lib/use-websocket-notifications";

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  useWebSocketNotifications(user?.id ?? null);
  return <>{children}</>;
}
