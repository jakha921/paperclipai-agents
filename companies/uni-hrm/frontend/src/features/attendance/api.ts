import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type {
  AttendanceFilters,
  AttendanceRecord,
  TimeSheet,
  WorkSchedule,
  WorkScheduleCreateData,
} from './types';

const BASE = '/attendance';

export function useWorkSchedules() {
  return useQuery<WorkSchedule[]>({
    queryKey: ['work-schedules'],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/schedules/');
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useCreateWorkSchedule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: WorkScheduleCreateData) => {
      const res = await apiClient.post(BASE + '/schedules/', data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['work-schedules'] }),
  });
}

export function useUpdateWorkSchedule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<WorkScheduleCreateData> }) => {
      const res = await apiClient.patch(`${BASE}/schedules/${id}/`, data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['work-schedules'] }),
  });
}

export function useDeleteWorkSchedule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${BASE}/schedules/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['work-schedules'] }),
  });
}

export function useAttendanceRecords(filters?: AttendanceFilters) {
  return useQuery<AttendanceRecord[]>({
    queryKey: ['attendance-records', filters],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/records/', { params: filters });
      return data.results ?? data;
    },
  });
}

export function useCreateAttendanceRecord() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (
      data: Omit<AttendanceRecord, 'id' | 'worked_hours' | 'overtime_hours'>,
    ) => {
      const res = await apiClient.post(BASE + '/records/', data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['attendance-records'] }),
  });
}

export function useUpdateAttendanceRecord() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<AttendanceRecord> }) => {
      const res = await apiClient.patch(`${BASE}/records/${id}/`, data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['attendance-records'] }),
  });
}

export function useBulkCreateAttendance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (
      records: Omit<AttendanceRecord, 'id' | 'worked_hours' | 'overtime_hours'>[],
    ) => {
      const res = await apiClient.post(BASE + '/records/bulk_create/', { records });
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['attendance-records'] }),
  });
}

export function useTimeSheets(filters?: {
  employee?: string;
  month?: number;
  year?: number;
  status?: string;
}) {
  return useQuery<TimeSheet[]>({
    queryKey: ['timesheets', filters],
    queryFn: async () => {
      const { data } = await apiClient.get(BASE + '/timesheets/', { params: filters });
      return data.results ?? data;
    },
  });
}

export function useTimeSheet(id: string) {
  return useQuery<TimeSheet>({
    queryKey: ['timesheet', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`${BASE}/timesheets/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useSubmitTimeSheet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post(`${BASE}/timesheets/${id}/submit/`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['timesheets'] }),
  });
}

export function useApproveTimeSheet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post(`${BASE}/timesheets/${id}/approve/`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['timesheets'] }),
  });
}
