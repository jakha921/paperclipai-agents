import { useEffect, useRef } from 'react';
import { useNotificationStore } from './store';
import type { Notification } from './types';

export function useNotificationSocket(token: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const addNotification = useNotificationStore((s) => s.addNotification);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!token) return;

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname;
      const ws = new WebSocket(
        `${protocol}//${host}:8000/ws/notifications/?token=${token}`,
      );
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const notification = JSON.parse(event.data as string) as Notification;
          addNotification(notification);
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        reconnectTimerRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      wsRef.current?.close();
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [token, addNotification]);
}
