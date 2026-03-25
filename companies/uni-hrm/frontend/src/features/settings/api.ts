import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type { SystemSettings, UpdateSettingsData, TestEmailRequest, TestEmailResponse } from './types';

export function useSystemSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const { data } = await apiClient.get<SystemSettings>('/settings/');
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: UpdateSettingsData) => {
      const { data } = await apiClient.patch<SystemSettings>('/settings/', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });
}

export function useTestEmail() {
  return useMutation({
    mutationFn: async (payload: TestEmailRequest) => {
      const { data } = await apiClient.post<TestEmailResponse>('/settings/test_email/', payload);
      return data;
    },
  });
}
