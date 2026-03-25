import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type {
  LeaveBalance,
  LeaveCalendarEvent,
  LeaveRequest,
  LeaveRequestCreateData,
  LeaveType,
  PublicHoliday,
} from './types';

const BASE = '/leaves';

export function useLeaveTypes() {
  return useQuery<LeaveType[]>({
    queryKey: ['leave-types'],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/types/');
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useLeaveBalance(year?: number) {
  return useQuery<LeaveBalance[]>({
    queryKey: ['leave-balance', year],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/requests/balance/', {
        params: year ? { year } : {},
      });
      return data;
    },
  });
}

export function useLeaveRequests(filters?: Record<string, string>) {
  return useQuery<LeaveRequest[]>({
    queryKey: ['leave-requests', filters],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/requests/', { params: filters });
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useLeaveRequest(id: string) {
  return useQuery<LeaveRequest>({
    queryKey: ['leave-request', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`${BASE}/requests/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateLeaveRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: LeaveRequestCreateData) => {
      const res = await apiClient.post(BASE + '/requests/', data);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leave-requests'] });
      qc.invalidateQueries({ queryKey: ['leave-balance'] });
    },
  });
}

export function useSubmitLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post(`${BASE}/requests/${id}/submit/`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leave-requests'] }),
  });
}

export function useApproveLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post(`${BASE}/requests/${id}/approve/`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leave-requests'] }),
  });
}

export function useRejectLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, rejection_reason }: { id: string; rejection_reason: string }) => {
      const res = await apiClient.post(`${BASE}/requests/${id}/reject/`, { rejection_reason });
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leave-requests'] }),
  });
}

export function useCancelLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post(`${BASE}/requests/${id}/cancel/`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leave-requests'] }),
  });
}

export function useLeaveCalendar(params: {
  department?: string;
  month?: string;
  year?: string;
}) {
  return useQuery<LeaveCalendarEvent[]>({
    queryKey: ['leave-calendar', params],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/requests/calendar/', { params });
      return data;
    },
  });
}

export function usePublicHolidays(year?: number) {
  return useQuery<PublicHoliday[]>({
    queryKey: ['public-holidays', year],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/holidays/', {
        params: year ? { year } : {},
      });
      return data.results ?? data;
    },
  });
}
