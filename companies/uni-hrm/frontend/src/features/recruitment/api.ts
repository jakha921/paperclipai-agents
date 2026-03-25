import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type {
  CandidateDetail,
  CandidateListItem,
  CreateCandidateData,
  CreateInterviewData,
  CreateVacancyData,
  Interview,
  PaginatedResponse,
  Vacancy,
} from './types';

// --- Vacancies ---

export function useVacancies(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['vacancies', params],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<Vacancy>>(
        '/recruitment/vacancies/',
        { params },
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useVacancy(id: string) {
  return useQuery({
    queryKey: ['vacancy', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Vacancy>(`/recruitment/vacancies/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateVacancy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateVacancyData) => {
      const { data } = await apiClient.post<Vacancy>('/recruitment/vacancies/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vacancies'] }),
  });
}

export function useUpdateVacancy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CreateVacancyData> }) => {
      const res = await apiClient.patch<Vacancy>(`/recruitment/vacancies/${id}/`, data);
      return res.data;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['vacancies'] });
      qc.invalidateQueries({ queryKey: ['vacancy', vars.id] });
    },
  });
}

export function usePublishVacancy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ status: string }>(
        `/recruitment/vacancies/${id}/publish/`,
      );
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vacancies'] }),
  });
}

export function useCloseVacancy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ status: string }>(
        `/recruitment/vacancies/${id}/close/`,
      );
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vacancies'] }),
  });
}

// --- Candidates ---

export function useCandidates(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['candidates', params],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<CandidateListItem>>(
        '/recruitment/candidates/',
        { params },
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCandidate(id: string) {
  return useQuery({
    queryKey: ['candidate', id],
    queryFn: async () => {
      const { data } = await apiClient.get<CandidateDetail>(`/recruitment/candidates/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateCandidate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateCandidateData) => {
      const { data } = await apiClient.post<CandidateListItem>(
        '/recruitment/candidates/',
        payload,
      );
      return data;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['candidates'] });
      qc.invalidateQueries({ queryKey: ['vacancy', vars.vacancy] });
    },
  });
}

export function useHireCandidate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ employee_id: string }>(
        `/recruitment/candidates/${id}/hire/`,
      );
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['candidates'] });
      qc.invalidateQueries({ queryKey: ['employees'] });
      qc.invalidateQueries({ queryKey: ['vacancies'] });
    },
  });
}

export function useRejectCandidate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ stage: string }>(
        `/recruitment/candidates/${id}/reject/`,
      );
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['candidates'] });
      qc.invalidateQueries({ queryKey: ['vacancies'] });
    },
  });
}

// --- Interviews ---

export function useInterviews(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['interviews', params],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<Interview>>(
        '/recruitment/interviews/',
        { params },
      );
      return data;
    },
  });
}

export function useCreateInterview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateInterviewData) => {
      const { data } = await apiClient.post<Interview>('/recruitment/interviews/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['interviews'] }),
  });
}
