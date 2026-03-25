export interface SystemSettings {
  id: number;
  site_name: string;
  site_url: string;
  working_hours_start: string;
  working_hours_end: string;
  working_days: number[];
  annual_leave_days: number;
  sick_leave_days: number;
  currency: string;
  timezone: string;
  smtp_host: string;
  smtp_port: number;
  smtp_use_tls: boolean;
  smtp_username: string;
  from_email: string;
  created_at: string;
  updated_at: string;
}

export type UpdateSettingsData = Partial<
  Omit<SystemSettings, 'id' | 'created_at' | 'updated_at'>
>;

export interface TestEmailRequest {
  to_email: string;
}

export interface TestEmailResponse {
  message?: string;
  error?: string;
}
