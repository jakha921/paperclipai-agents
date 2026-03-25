export interface WorkSchedule {
  id: string;
  name: string;
  schedule_type: '5/2' | '6/1' | 'SHIFT' | 'FLEXIBLE';
  work_start: string;
  work_end: string;
  break_start: string | null;
  break_end: string | null;
  working_days: number[];
}

export interface EmployeeSchedule {
  id: string;
  employee: string;
  schedule: WorkSchedule;
  effective_from: string;
  effective_to: string | null;
}

export type AttendanceStatus =
  | 'PRESENT'
  | 'ABSENT'
  | 'LATE'
  | 'HALF_DAY'
  | 'ON_LEAVE'
  | 'HOLIDAY';

export type TimesheetStatus = 'DRAFT' | 'SUBMITTED' | 'APPROVED';

export interface AttendanceRecord {
  id: string;
  employee: string;
  date: string;
  check_in: string | null;
  check_out: string | null;
  status: AttendanceStatus;
  worked_hours: string;
  overtime_hours: string;
  source: string;
  note: string;
}

export interface TimeSheet {
  id: string;
  employee: string;
  month: number;
  year: number;
  total_working_days: number;
  days_present: number;
  days_absent: number;
  days_late: number;
  days_on_leave: number;
  total_hours: string;
  overtime_hours: string;
  status: TimesheetStatus;
  approved_by: string | null;
}

export interface AttendanceFilters {
  employee?: string;
  date_from?: string;
  date_to?: string;
  status?: string;
  department?: string;
}

export interface WorkScheduleCreateData {
  name: string;
  schedule_type: '5/2' | '6/1' | 'SHIFT' | 'FLEXIBLE';
  work_start: string;
  work_end: string;
  break_start?: string;
  break_end?: string;
  working_days: number[];
}
