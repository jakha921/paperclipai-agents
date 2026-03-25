import { useState, useEffect } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { cn } from '@/shared/lib/utils';
import { PageHeader, Button, Tabs, EmptyState, Skeleton, Card } from '@/shared/ui';
import {
  useNotifications,
  useMarkRead,
  useMarkAllRead,
  useNotificationStore,
} from '@/features/notifications';

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

const tabs = [
  { value: 'all', label: 'Все' },
  { value: 'unread', label: 'Непрочитанные' },
];

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState('all');

  const params = activeTab === 'unread' ? { is_read: false } : undefined;
  const { data, isLoading } = useNotifications(params);
  const markReadMutation = useMarkRead();
  const markAllReadMutation = useMarkAllRead();

  const storeMarkRead = useNotificationStore((s) => s.markRead);
  const storeMarkAllRead = useNotificationStore((s) => s.markAllRead);
  const setNotifications = useNotificationStore((s) => s.setNotifications);

  useEffect(() => {
    if (data?.results) {
      setNotifications(data.results);
    }
  }, [data, setNotifications]);

  function handleMarkRead(id: string) {
    storeMarkRead(id);
    markReadMutation.mutate(id);
  }

  function handleMarkAllRead() {
    storeMarkAllRead();
    markAllReadMutation.mutate();
  }

  const notifications = data?.results ?? [];

  return (
    <div>
      <PageHeader
        title="Уведомления"
        description="Управление уведомлениями"
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={handleMarkAllRead}
            disabled={markAllReadMutation.isPending}
          >
            <CheckCheck className="h-4 w-4" />
            Прочитать все
          </Button>
        }
      />

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} className="mb-6" />

      <Card>
        {isLoading ? (
          <div className="p-6 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="h-9 w-9 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-72" />
                </div>
              </div>
            ))}
          </div>
        ) : notifications.length === 0 ? (
          <EmptyState
            icon={<Bell className="h-12 w-12" />}
            title={activeTab === 'unread' ? 'Нет непрочитанных' : 'Нет уведомлений'}
            description="Когда появятся новые уведомления, вы увидите их здесь"
          />
        ) : (
          <div className="divide-y divide-slate-100">
            {notifications.map((n) => (
              <button
                key={n.id}
                onClick={() => {
                  if (!n.is_read) handleMarkRead(n.id);
                }}
                className={cn(
                  'w-full text-left px-6 py-4 hover:bg-slate-50 transition-colors flex items-start gap-4',
                  !n.is_read && 'bg-indigo-50/50',
                )}
              >
                <div
                  className={cn(
                    'mt-0.5 rounded-lg p-2',
                    !n.is_read
                      ? 'bg-primary-100 text-primary-600'
                      : 'bg-slate-100 text-slate-400',
                  )}
                >
                  <Bell className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p
                      className={cn(
                        'text-sm',
                        !n.is_read ? 'font-semibold text-slate-900' : 'font-medium text-slate-700',
                      )}
                    >
                      {n.title}
                    </p>
                    {!n.is_read && (
                      <div className="h-2 w-2 rounded-full bg-primary-500 shrink-0" />
                    )}
                  </div>
                  <p className="text-sm text-slate-500 mt-0.5">{n.message}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {formatRelativeTime(n.created_at)}
                  </p>
                </div>
              </button>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
