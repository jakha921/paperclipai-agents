export interface AcademicDegree {
  id: number;
  name: Record<string, string>;
  code: string;
  country: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicTitle {
  id: number;
  name: Record<string, string>;
  code: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeAcademic {
  id: number;
  employee: number;
  degree: number | null;
  degree_detail?: AcademicDegree;
  title: number | null;
  title_detail?: AcademicTitle;
  specialization: string;
  dissertation_topic: string;
  diploma_number: string;
  awarded_date: string | null;
  created_at: string;
  updated_at: string;
}

export type LoadType = 'PRIMARY' | 'ADDITIONAL';

export interface Subject {
  id: number;
  name: Record<string, string>;
  code: string;
  department: number;
  credits: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AcademicLoad {
  id: number;
  employee: number;
  subject: number;
  subject_detail?: Subject;
  academic_year: string;
  semester: 1 | 2;
  lecture_hours: number;
  seminar_hours: number;
  lab_hours: number;
  total_hours: number;
  load_type: LoadType;
  created_at: string;
  updated_at: string;
}

export type ContestStatus = 'OPEN' | 'REVIEWING' | 'CLOSED';

export interface PositionContest {
  id: number;
  department: number;
  position: number;
  requirements: string;
  application_deadline: string;
  status: ContestStatus;
  winner: number | null;
  created_at: string;
  updated_at: string;
}

export interface AcademicLoadSummary {
  total_hours: number;
  by_semester: Record<number, number>;
  by_subject: Record<string, number>;
  exceeds_limit: boolean;
}
