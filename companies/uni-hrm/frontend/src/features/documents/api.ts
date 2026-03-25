import { apiClient } from '@/shared/lib/api-client';
import type {
  DocumentTemplate,
  GeneratedDocument,
  GenerateDocumentRequest,
  DashboardStats,
  TurnoverStat,
  DepartmentStat,
  Demographics,
} from './types';

// Templates
export const fetchTemplates = () =>
  apiClient
    .get<{ results: DocumentTemplate[] } | DocumentTemplate[]>('/documents/templates/')
    .then((r) => (Array.isArray(r.data) ? r.data : (r.data as { results: DocumentTemplate[] }).results));

// Generated Documents
export const fetchGeneratedDocuments = (filters?: { employee?: string }) =>
  apiClient
    .get<GeneratedDocument[]>('/documents/documents/', { params: filters })
    .then((r) => r.data);

export const generateDocument = (data: GenerateDocumentRequest) =>
  apiClient.post<GeneratedDocument>('/documents/documents/generate/', data).then((r) => r.data);

export const downloadDocument = (id: string) =>
  apiClient
    .get<Blob>(`/documents/documents/${id}/download/`, { responseType: 'blob' })
    .then((r) => r.data);

// Reports
export const downloadPayrollExcel = (params: {
  period_id?: string;
  department_id?: string;
}) =>
  apiClient
    .post<Blob>('/documents/reports/payroll_excel/', params, { responseType: 'blob' })
    .then((r) => r.data);

export const downloadEmployeesExcel = (params: {
  department_id?: string;
  status?: string;
}) =>
  apiClient
    .post<Blob>('/documents/reports/employees_excel/', params, { responseType: 'blob' })
    .then((r) => r.data);

// Analytics
export const fetchDashboardStats = () =>
  apiClient.get<DashboardStats>('/documents/analytics/dashboard/').then((r) => r.data);

export const fetchTurnoverStats = (months = 12) =>
  apiClient
    .get<TurnoverStat[]>('/documents/analytics/turnover/', { params: { months } })
    .then((r) => r.data);

export const fetchDepartmentStats = () =>
  apiClient.get<DepartmentStat[]>('/documents/analytics/departments/').then((r) => r.data);

export const fetchDemographics = () =>
  apiClient.get<Demographics>('/documents/analytics/demographics/').then((r) => r.data);
