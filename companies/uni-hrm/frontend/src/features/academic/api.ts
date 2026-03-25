import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type {
  AcademicDegree,
  AcademicTitle,
  EmployeeAcademic,
  Subject,
  AcademicLoad,
  AcademicLoadSummary,
  PositionContest,
} from './types';

// Degrees
export function useAcademicDegrees() {
  return useQuery({
    queryKey: ['academic', 'degrees'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: AcademicDegree[]; count: number }>(
        '/academic/degrees/',
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

// Titles
export function useAcademicTitles() {
  return useQuery({
    queryKey: ['academic', 'titles'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: AcademicTitle[]; count: number }>(
        '/academic/titles/',
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

// Employee Academic
export function useEmployeeAcademic(employeeId: string | number) {
  return useQuery({
    queryKey: ['academic', 'employee-academic', employeeId],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: EmployeeAcademic[]; count: number }>(
        '/academic/employee-academic/',
        { params: { employee: employeeId } },
      );
      return data;
    },
    enabled: !!employeeId,
  });
}

// Subjects
export function useSubjects(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['academic', 'subjects', params],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: Subject[]; count: number }>(
        '/academic/subjects/',
        { params },
      );
      return data;
    },
  });
}

// Academic Loads
export function useAcademicLoads(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['academic', 'loads', params],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: AcademicLoad[]; count: number }>(
        '/academic/loads/',
        { params },
      );
      return data;
    },
  });
}

// Academic Load Summary
export function useAcademicLoadSummary(employeeId: string | number, academicYear: string) {
  return useQuery({
    queryKey: ['academic', 'loads', 'summary', employeeId, academicYear],
    queryFn: async () => {
      const { data } = await apiClient.get<AcademicLoadSummary>(
        `/academic/loads/summary/`,
        { params: { employee: employeeId, academic_year: academicYear } },
      );
      return data;
    },
    enabled: !!employeeId && !!academicYear,
  });
}

// Position Contests
export function usePositionContests(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['academic', 'contests', params],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: PositionContest[]; count: number }>(
        '/academic/contests/',
        { params },
      );
      return data;
    },
  });
}

// Mutations
export function useCreateAcademicLoad() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Omit<AcademicLoad, 'id' | 'total_hours' | 'subject_detail' | 'created_at' | 'updated_at'>) => {
      const res = await apiClient.post<AcademicLoad>('/academic/loads/', payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic', 'loads'] });
    },
  });
}

export function useUpdateAcademicLoad() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<AcademicLoad> }) => {
      const res = await apiClient.patch<AcademicLoad>(`/academic/loads/${id}/`, data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic', 'loads'] });
    },
  });
}

export function useCloseContest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const res = await apiClient.post<PositionContest>(`/academic/contests/${id}/close/`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic', 'contests'] });
    },
  });
}

export function useSetContestWinner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, winnerId }: { id: number; winnerId: number }) => {
      const res = await apiClient.post<PositionContest>(
        `/academic/contests/${id}/set_winner/`,
        { winner: winnerId },
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic', 'contests'] });
    },
  });
}
