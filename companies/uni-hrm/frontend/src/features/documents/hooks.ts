import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from './api';
import type { GenerateDocumentRequest } from './types';

export const useDocumentTemplates = () =>
  useQuery({ queryKey: ['document-templates'], queryFn: api.fetchTemplates });

export const useGeneratedDocuments = (filters?: { employee?: string }) =>
  useQuery({
    queryKey: ['generated-documents', filters],
    queryFn: () => api.fetchGeneratedDocuments(filters),
  });

export const useGenerateDocument = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: GenerateDocumentRequest) => api.generateDocument(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['generated-documents'] }),
  });
};

export const useDownloadDocument = () =>
  useMutation({ mutationFn: (id: string) => api.downloadDocument(id) });

export const useDashboardStats = () =>
  useQuery({ queryKey: ['dashboard-stats'], queryFn: api.fetchDashboardStats });

export const useTurnoverStats = (months = 12) =>
  useQuery({
    queryKey: ['turnover-stats', months],
    queryFn: () => api.fetchTurnoverStats(months),
  });

export const useDepartmentStats = () =>
  useQuery({ queryKey: ['department-stats'], queryFn: api.fetchDepartmentStats });

export const useDemographics = () =>
  useQuery({ queryKey: ['demographics'], queryFn: api.fetchDemographics });

export const useDownloadPayrollExcel = () =>
  useMutation({
    mutationFn: (params: { period_id?: string; department_id?: string }) =>
      api.downloadPayrollExcel(params),
  });

export const useDownloadEmployeesExcel = () =>
  useMutation({
    mutationFn: (params: { department_id?: string; status?: string }) =>
      api.downloadEmployeesExcel(params),
  });
