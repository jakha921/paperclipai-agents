import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type { Department, Position, CreateDepartmentData, CreatePositionData } from './types';

// Departments
export function useDepartments(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['departments', params],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: Department[]; count: number }>(
        '/departments/',
        { params },
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useDepartmentTree() {
  return useQuery({
    queryKey: ['departments', 'tree'],
    queryFn: async () => {
      const { data } = await apiClient.get<Department[]>('/departments/tree/');
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useOrgChart() {
  return useQuery({
    queryKey: ['departments', 'org-chart'],
    queryFn: async () => {
      const { data } = await apiClient.get<
        Array<{
          id: string;
          name: string;
          code: string;
          type: string;
          parentId: string | null;
          employee_count: number;
          head_name: string | null;
        }>
      >('/departments/org_chart/');
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useDepartment(id: string) {
  return useQuery({
    queryKey: ['departments', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Department>(`/departments/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateDepartmentData) => {
      const res = await apiClient.post<Department>('/departments/', data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}

export function useUpdateDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CreateDepartmentData> }) => {
      const res = await apiClient.patch<Department>(`/departments/${id}/`, data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}

export function useDeleteDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/departments/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}

// Positions
export function usePositions(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['positions', params],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: Position[]; count: number }>('/positions/', {
        params,
      });
      return data;
    },
  });
}

export function useCreatePosition() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreatePositionData) => {
      const res = await apiClient.post<Position>('/positions/', data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });
}

export function useUpdatePosition() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CreatePositionData> }) => {
      const res = await apiClient.patch<Position>(`/positions/${id}/`, data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });
}

export function useDeletePosition() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/positions/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });
}
