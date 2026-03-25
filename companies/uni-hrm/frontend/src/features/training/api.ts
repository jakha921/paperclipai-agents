import type { TrainingProgram, Enrollment, EnrollCourseRequest } from './types';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchPrograms(): Promise<TrainingProgram[]> {
  const res = await fetch(`${API_BASE}/api/v1/training/programs/`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch training programs');
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function fetchMyEnrollments(): Promise<Enrollment[]> {
  const res = await fetch(`${API_BASE}/api/v1/training/enrollments/`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch enrollments');
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function enrollCourse(data: EnrollCourseRequest): Promise<Enrollment> {
  const res = await fetch(`${API_BASE}/api/v1/training/enrollments/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to enroll in course');
  return res.json();
}
