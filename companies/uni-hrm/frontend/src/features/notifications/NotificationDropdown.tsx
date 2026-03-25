import { Link } from 'react-router-dom';
import { Bell, CheckCheck } from 'lucide-react';
import { cn } from '@/shared/lib/utils';
import { useNotificationStore } from './store';
import { useNotifications, useMarkRead, useMarkAllRead } from './api';
import { useEffect } from 'react';

function formatRelativeTime(dateStr: string): string {
  const now = Date.now();
  const date = new Date(dateStr).getTime();
  const diffSec = Math.floor((now - date) / 1000);

  if (diffSec < 60) return 'только что';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} мин. назад`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} ч. назад`;
  if (diffSec < 604800) return `${Math.floor(diffSec / 86400)} дн. назад`;
  return new Date(dateStr).toLocaleDateString('ru-RU');
}

interface NotificationDropdownProps {
  onClose: () => void;
}

export function NotificationDropdown({ onClose }: NotificationDropdownProps) {
  const storeNotifications = useNotificationStore((s) => s.notifications);
  const storeMarkRead = useNotificationStore((s) => s.markRead);
  const storeMarkAllRead = useNotificationStore((s) => s.markAllRead);
  const setNotifications = useNotificationStore((s) => s.setNotifications);

  const { data } = useNotifications();
  const markReadMutation = useMarkRead();
  const markAllReadMutation = useMarkAllRead();

  useEffect(() => {
    if (data?.results) {
      setNotifications(data.results);
    }
  }, [data, setNotifications]);

  const notifications = storeNotifications.slice(0, 5);

  function handleMarkRead(id: string) {
    storeMarkRead(id);
    markReadMutation.mutate(id);
  }

  function handleMarkAllRead() {
    storeMarkAllRead();
    markAllReadMutation.mutate();
  }

  return (
    <div className="absolute right-0 top-full mt-2 w-80 bg-white shadow-md rounded-xl border border-slate-200 z-50">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
        <h3 className="text-sm font-semibold text-slate-900">Уведомления</h3>
        <button
          onClick={handleMarkAllRead}
          className="flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors"
        >
          <CheckCheck className="h-3.5 w-3.5" />
          Прочитать все
        </button>
      </div>

      <div className="max-h-80 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="py-8 text-center text-sm text-slate-500">
            Нет уведомлений
          </div>
        ) : (
          notifications.map((n) => (
            <button
              key={n.id}
              onClick={() => {
                if (!n.is_read) handleMarkRead(n.id);
              }}
              className={cn(
                'w-full text-left px-4 py-3 border-b border-slate-50 hover:bg-slate-50 transition-colors',
                !n.is_read && 'bg-indigo-50/50',
              )}
            >
              <div className="flex items-start gap-3">
                <div
                  className={cn(
                    'mt-0.5 rounded-lg p-1.5',
                    !n.is_read
                      ? 'bg-primary-100 text-primary-600'
                      : 'bg-slate-100 text-slate-400',
                  )}
                >
                  <Bell className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      'text-sm truncate',
                      !n.is_read ? 'font-semibold text-slate-900' : 'font-medium text-slate-700',
                    )}
                  >
                    {n.title}
                  </p>
                  <p className="text-xs text-slate-500 truncate mt-0.5">{n.message}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {formatRelativeTime(n.created_at)}
                  </p>
                </div>
                {!n.is_read && (
                  <div className="mt-2 h-2 w-2 rounded-full bg-primary-500 shrink-0" />
                )}
              </div>
            </button>
          ))
        )}
      </div>

      <div className="border-t border-slate-100 px-4 py-2.5">
        <Link
          to="/notifications"
          onClick={onClose}
          className="block text-center text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
        >
          Все уведомления
        </Link>
      </div>
    </div>
  );
}
