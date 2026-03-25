export interface TaxConfiguration {
  id: number;
  year: number;
  ndfl_rate: string;
  social_tax_rate: string;
  inps_employee_rate: string;
  inps_employer_rate: string;
  minimum_wage: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeSalary {
  id: number;
  employee: number;
  effective_from: string;
  effective_to: string | null;
  base_salary: string;
  academic_bonus_pct: string;
  position_bonus_pct: string;
  seniority_bonus_pct: string;
  other_allowances: string;
  gross_monthly: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type PayrollStatus = 'DRAFT' | 'CALCULATED' | 'APPROVED' | 'PAID';

export interface Payroll {
  id: number;
  employee: number;
  employee_name: string;
  month: number;
  year: number;
  tax_config: number;
  base_salary: string;
  academic_bonus: string;
  position_bonus: string;
  seniority_bonus: string;
  other_allowances: string;
  working_days_in_month: number;
  days_worked: number;
  days_on_leave: number;
  days_absent: number;
  overtime_hours: string;
  attendance_ratio: string;
  overtime_payment: string;
  gross_salary: string;
  ndfl: string;
  inps_employee: string;
  other_deductions: string;
  total_deductions: string;
  net_salary: string;
  employer_social_tax: string;
  employer_inps: string;
  status: PayrollStatus;
  approved_by: number | null;
  paid_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface BulkCalculateRequest {
  month: number;
  year: number;
}

export interface BulkCalculateResult {
  calculated: number;
  errors: number;
  results: Array<{ employee: string; payroll_id: number; net_salary: string }>;
  error_details: Array<{ employee: string; error: string }>;
}
