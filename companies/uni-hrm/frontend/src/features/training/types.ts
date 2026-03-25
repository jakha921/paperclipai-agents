export interface TrainingProgram {
  id: number;
  title: string;
  description: string;
  duration_hours: number;
  category: string;
  is_active: boolean;
  created_at: string;
}

export interface Enrollment {
  id: number;
  program: number;
  program_title: string;
  enrolled_at: string;
  status: 'enrolled' | 'in_progress' | 'completed' | 'cancelled';
  completed_at: string | null;
}

export type EnrollCourseRequest = {
  program: number;
};
