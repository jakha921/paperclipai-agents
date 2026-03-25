export type AppraisalCycleStatus = 'planning' | 'active' | 'review' | 'completed';
export type EmployeeAppraisalStatus = 'pending' | 'self_review' | 'manager_review' | 'completed';
export type TrainingStatus = 'enrolled' | 'in_progress' | 'completed' | 'cancelled';
export type TrainingType = 'internal' | 'external' | 'online';
export type KPICategory = 'academic' | 'administrative' | 'research' | 'service';

export interface AppraisalCycle {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: AppraisalCycleStatus;
  applicable_departments: string[];
  created_at: string;
}

export interface KPIIndicator {
  id: string;
  name: Record<string, string>;
  description: string;
  category: KPICategory;
  weight: string;
  max_score: number;
  created_at: string;
}

export interface EmployeeAppraisal {
  id: string;
  cycle: string;
  cycle_name?: string;
  employee: string;
  employee_name?: string;
  reviewer: string | null;
  status: EmployeeAppraisalStatus;
  overall_score: string | null;
  comments: string;
  reviewed_at: string | null;
  created_at: string;
}

export interface AppraisalScore {
  id: string;
  appraisal: string;
  kpi: string;
  kpi_name?: Record<string, string>;
  self_score: number | null;
  manager_score: number | null;
  final_score: string | null;
  comment: string;
}

export interface TrainingProgram {
  id: string;
  name: Record<string, string>;
  description: string;
  provider: string;
  training_type: TrainingType;
  duration_hours: number;
  cost: string;
  is_active: boolean;
  created_at: string;
}

export interface TrainingRecord {
  id: string;
  employee: string;
  employee_name?: string;
  program: string;
  program_name?: Record<string, string>;
  start_date: string | null;
  end_date: string | null;
  status: TrainingStatus;
  certificate_number: string;
  score: number | null;
  created_at: string;
}
