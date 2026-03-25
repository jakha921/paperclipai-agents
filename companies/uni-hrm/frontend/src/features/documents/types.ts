export interface DocumentTemplate {
  id: string;
  name: string;
  code: string;
  output_format: 'pdf' | 'docx';
  variables_schema: Record<string, { type: string; label: string }>;
  is_active: boolean;
  created_at: string;
}

export interface GeneratedDocument {
  id: string;
  template: string;
  template_name: string;
  employee: string;
  employee_name: string;
  file_url: string | null;
  data: Record<string, unknown>;
  generated_at: string;
}

export interface GenerateDocumentRequest {
  template_code: string;
  employee_id: string;
  extra_data?: Record<string, unknown>;
}

export interface DashboardStats {
  total_employees: number;
  total_departments: number;
  open_vacancies: number;
  pending_leaves: number;
  total_payroll_last_month: number;
  avg_salary: number;
  new_hires_this_month: number;
}

export interface TurnoverStat {
  month: string;
  hired_count: number;
  dismissed_count: number;
  turnover_rate: number;
}

export interface DepartmentStat {
  id: string;
  name: string;
  employee_count: number;
  avg_salary: number;
  open_vacancies: number;
}

export interface Demographics {
  total: number;
  gender_distribution: Record<string, number>;
  age_groups: Record<string, number>;
  education_levels: Record<string, number>;
  experience_groups: Record<string, number>;
}
