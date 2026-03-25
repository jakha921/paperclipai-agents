export interface Notification {
  id: string;
  title: string;
  message: string;
  channel: 'in_app' | 'email' | 'telegram';
  is_read: boolean;
  read_at: string | null;
  data: Record<string, unknown>;
  created_at: string;
}

export interface UnreadCountResponse {
  count: number;
}

export interface NotificationsResponse {
  results: Notification[];
  count: number;
}
