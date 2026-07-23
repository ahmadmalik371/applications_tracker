/**
 * useWebSocketNotifications
 *
 * Connects to the backend WebSocket endpoint at /ws/notifications/{userId}.
 * On receiving any JSON message from the server the hook invalidates the
 * TanStack Query cache for ["notifications"] so the UI refreshes automatically.
 *
 * Features:
 *  - Automatic ping/pong keepalive (every 25 s)
 *  - Exponential-backoff reconnect (up to MAX_RETRIES = 5)
 *  - Graceful cleanup on unmount
 *  - No-op when userId is not yet available
 */

import { useEffect, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";

const WS_BASE =
  process.env.NEXT_PUBLIC_WS_URL ||
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${
        process.env.NEXT_PUBLIC_API_HOST || "localhost:8000"
      }`
    : "ws://localhost:8000");

const PING_INTERVAL_MS = 25_000;
const INITIAL_RECONNECT_DELAY_MS = 1_000;
const MAX_RETRIES = 5;

export function useWebSocketNotifications(userId: string | null | undefined) {
  const qc = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const pingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryCountRef = useRef(0);
  const isMountedRef = useRef(true);

  const clearPing = () => {
    if (pingTimerRef.current) {
      clearInterval(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  };

  const clearReconnect = () => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const connect = useCallback(() => {
    if (!userId || !isMountedRef.current) return;

    const url = `${WS_BASE}/ws/notifications/${userId}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        retryCountRef.current = 0; // reset backoff on successful connect

        // Start keepalive pings
        clearPing();
        pingTimerRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
          }
        }, PING_INTERVAL_MS);
      };

      ws.onmessage = (event) => {
        // Ignore pong keepalive responses
        if (event.data === "pong") return;

        // Any other message from the server means a new notification event —
        // invalidate the query cache so the notification list refreshes.
        qc.invalidateQueries({ queryKey: ["notifications"] });
        qc.invalidateQueries({ queryKey: ["unread-count"] });
      };

      ws.onclose = () => {
        clearPing();

        // Attempt reconnection with exponential backoff
        if (isMountedRef.current && retryCountRef.current < MAX_RETRIES) {
          const delay =
            INITIAL_RECONNECT_DELAY_MS * Math.pow(2, retryCountRef.current);
          retryCountRef.current += 1;
          reconnectTimerRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        // onclose will fire after onerror; reconnect logic lives there.
        ws.close();
      };
    } catch {
      // WebSocket constructor can throw in SSR / unsupported environments.
      // Silently ignore.
    }
  }, [userId, qc]);

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      clearPing();
      clearReconnect();

      if (wsRef.current) {
        // Close without triggering auto-reconnect (isMountedRef is false)
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Re-connect when userId changes (login / logout)
}
