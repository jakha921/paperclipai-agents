export interface VacancyTitle {
  ru?: string;
  uz?: string;
  en?: string;
}

export type VacancyStatus = 'DRAFT' | 'OPEN' | 'CLOSED';
export type CandidateSource = 'EXTERNAL' | 'INTERNAL' | 'REFERRAL' | 'HEMIS';
export type CandidateStage =
  | 'APPLIED'
  | 'SCREENING'
  | 'INTERVIEW'
  | 'OFFER'
  | 'HIRED'
  | 'REJECTED';
export type InterviewType = 'HR' | 'TECHNICAL' | 'FINAL';
export type InterviewResult = 'PENDING' | 'PASS' | 'FAIL' | 'HOLD';

export interface Vacancy {
  id: string;
  title: VacancyTitle | string;
  department_name: string;
  status: VacancyStatus;
  vacancies_count: number;
  candidates_count: number;
  deadline: string | null;
  created_at: string;
  requirements?: string;
  responsibilities?: string;
  position?: string | null;
  position_name?: string | null;
  candidates?: CandidateListItem[];
}

export interface CandidateListItem {
  id: string;
  full_name: string;
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  stage: CandidateStage;
  source: CandidateSource;
  vacancy_title: string;
  applied_at: string;
}

export interface CandidateDetail extends CandidateListItem {
  middle_name: string;
  notes: string;
  resume: string | null;
  interviews: Interview[];
}

export interface Interview {
  id: string;
  interview_type: InterviewType;
  scheduled_at: string;
  result: InterviewResult;
  notes: string;
  duration_minutes: number;
  interviewer: string;
  interviewer_name: string;
}

export interface CreateVacancyData {
  title: VacancyTitle;
  department: string;
  position?: string | null;
  requirements?: string;
  responsibilities?: string;
  vacancies_count?: number;
  deadline?: string | null;
}

export interface CreateCandidateData {
  vacancy: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone: string;
  email?: string;
  source?: CandidateSource;
  notes?: string;
}

export interface CreateInterviewData {
  candidate: string;
  interviewer: string;
  scheduled_at: string;
  interview_type: InterviewType;
  notes?: string;
  duration_minutes?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
