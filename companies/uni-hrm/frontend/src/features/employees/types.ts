import type { Department, Position } from '../departments/types';

export interface Employee {
  id: string;
  employee_number: string;
  user: string | null;
  department: Department;
  position: Position;
  department_name: string;
  position_name: string;
  full_name: string;
  first_name: string;
  last_name: string;
  middle_name: string;
  hire_date: string;
  contract_type: 'PERMANENT' | 'PART_TIME' | 'HOURLY';
  status: 'ACTIVE' | 'ON_LEAVE' | 'DISMISSED';
  pinfl: string;
  inn: string | null;
  passport_series: string;
  birth_date: string;
  gender: 'MALE' | 'FEMALE';
  nationality: string;
  phone: string;
  email: string;
  address: string;
  photo: string | null;
  history?: EmploymentHistory[];
}

export interface EmploymentHistory {
  id: string;
  department: string;
  department_name: string;
  position: string;
  position_name: string;
  start_date: string;
  end_date: string | null;
  order_number: string;
  order_date: string;
  change_reason: 'HIRED' | 'TRANSFERRED' | 'PROMOTED' | 'DISMISSED';
}

export interface CreateEmployeeData {
  first_name: string;
  last_name: string;
  middle_name?: string;
  department: string;
  position: string;
  hire_date: string;
  contract_type: Employee['contract_type'];
  pinfl: string;
  inn?: string;
  passport_series: string;
  birth_date: string;
  gender: Employee['gender'];
  nationality: string;
  phone: string;
  email?: string;
  address?: string;
  user?: string;
}

export interface EmployeeFilters {
  department?: string;
  position?: string;
  status?: string;
  contract_type?: string;
  search?: string;
  page?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
