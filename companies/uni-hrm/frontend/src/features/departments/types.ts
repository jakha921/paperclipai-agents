export interface Department {
  id: string;
  name: Record<'ru' | 'uz' | 'en', string>;
  name_display: string;
  code: string;
  department_type: 'RECTORATE' | 'FACULTY' | 'DEPARTMENT' | 'ADMIN_SERVICE' | 'SUPPORT_UNIT';
  is_active: boolean;
  parent: string | null;
  employee_count: number;
  level: number;
  children?: Department[];
}

export interface Position {
  id: string;
  name: Record<'ru' | 'uz' | 'en', string>;
  code: string;
  category: 'PPS' | 'NS' | 'AUP' | 'UVP' | 'POP';
  min_salary: string | null;
  max_salary: string | null;
  is_academic: boolean;
  requirements: string;
  created_at: string;
}

export interface CreateDepartmentData {
  name: Record<'ru' | 'uz' | 'en', string>;
  code: string;
  department_type: Department['department_type'];
  parent?: string | null;
  is_active: boolean;
}

export interface CreatePositionData {
  name: Record<'ru' | 'uz' | 'en', string>;
  code: string;
  category: Position['category'];
  min_salary?: string | null;
  max_salary?: string | null;
  is_academic: boolean;
  requirements?: string;
}
