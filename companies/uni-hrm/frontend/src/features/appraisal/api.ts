import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type {
  AppraisalCycle,
  KPIIndicator,
  EmployeeAppraisal,
  AppraisalScore,
  TrainingProgram,
  TrainingRecord,
} from './types';

interface PaginatedResponse<T> {
  results: T[];
  count: number;
}

// Appraisal Cycles
export function useAppraisalCycles() {
  return useQuery({
    queryKey: ['appraisal-cycles'],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<AppraisalCycle>>(
        '/appraisals/cycles/',
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateAppraisalCycle() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<AppraisalCycle>) => {
      const { data } = await apiClient.post<AppraisalCycle>('/appraisals/cycles/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['appraisal-cycles'] }),
  });
}

// KPI Indicators
export function useKPIIndicators() {
  return useQuery({
    queryKey: ['kpi-indicators'],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<KPIIndicator>>(
        '/appraisals/kpis/',
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// Employee Appraisals
export function useEmployeeAppraisals(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['employee-appraisals', params],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<EmployeeAppraisal>>(
        '/appraisals/employee-appraisals/',
        { params },
      );
      return data;
    },
  });
}

export function useAppraisalScores(appraisalId: string) {
  return useQuery({
    queryKey: ['appraisal-scores', appraisalId],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<AppraisalScore>>(
        '/appraisals/scores/',
        { params: { appraisal: appraisalId } },
      );
      return data;
    },
    enabled: !!appraisalId,
  });
}

export function useSelfReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<EmployeeAppraisal>(
        `/appraisals/employee-appraisals/${id}/self-review/`,
      );
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['employee-appraisals'] }),
  });
}

export function useManagerReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<EmployeeAppraisal>(
        `/appraisals/employee-appraisals/${id}/manager-review/`,
      );
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['employee-appraisals'] }),
  });
}

export function useCompleteAppraisal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<EmployeeAppraisal>(
        `/appraisals/employee-appraisals/${id}/complete/`,
      );
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['employee-appraisals'] }),
  });
}

// Training Programs
export function useTrainingPrograms(params?: { is_active?: boolean }) {
  return useQuery({
    queryKey: ['training-programs', params],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<TrainingProgram>>(
        '/appraisals/training-programs/',
        { params },
      );
      return data;
    },
  });
}

// Training Records
export function useTrainingRecords(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['training-records', params],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<TrainingRecord>>(
        '/appraisals/training-records/',
        { params },
      );
      return data;
    },
  });
}

export function useEnrollTraining() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { employee: string; program: string }) => {
      const { data } = await apiClient.post<TrainingRecord>(
        '/appraisals/training-records/',
        payload,
      );
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['training-records'] }),
  });
}
