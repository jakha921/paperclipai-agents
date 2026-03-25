export interface LeaveType {
  id: string;
  name: Record<'ru' | 'uz' | 'en', string>;
  code: string;
  days_per_year: number;
  is_paid: boolean;
  requires_document: boolean;
  applicable_categories: string[];
}

export interface LeaveAllocation {
  id: string;
  employee: string;
  leave_type: LeaveType;
  year: number;
  total_days: number;
  used_days: number;
  carry_over_days: number;
  remaining_days: number;
}

export type LeaveStatus =
  | 'DRAFT'
  | 'PENDING_HEAD'
  | 'PENDING_HR'
  | 'APPROVED'
  | 'REJECTED'
  | 'CANCELLED';

export interface LeaveRequest {
  id: string;
  employee: string;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  days_count: number;
  reason: string;
  status: LeaveStatus;
  approved_by: string | null;
  rejection_reason: string;
  created_at: string;
}

export interface PublicHoliday {
  id: string;
  date: string;
  name: Record<'ru' | 'uz' | 'en', string>;
  is_working_day: boolean;
}

export interface LeaveBalance {
  leave_type: LeaveType;
  total_days: number;
  used_days: number;
  carry_over_days: number;
  remaining_days: number;
}

export interface LeaveCalendarEvent {
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
}

export interface LeaveRequestCreateData {
  leave_type_id: string;
  start_date: string;
  end_date: string;
  reason?: string;
}
