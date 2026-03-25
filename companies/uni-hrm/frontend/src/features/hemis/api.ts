import { apiClient } from '@/shared/lib/api-client';
import type { SyncLog, SyncConflict, SyncRequest, ResolveConflictRequest } from './types';

export const runSync = (data: SyncRequest) =>
  apiClient
    .post<{ task_id?: string; status: string }>('/integrations/hemis/sync/', data)
    .then((r) => r.data);

export const fetchHEMISStatus = () =>
  apiClient
    .get<SyncLog | { status: string; last_sync: null }>('/integrations/hemis/status_info/')
    .then((r) => r.data);

export const fetchSyncConflicts = (resolved?: boolean | null) => {
  const params: Record<string, string> = {};
  if (resolved === true) params.resolved = 'true';
  if (resolved === false) params.resolved = 'false';
  return apiClient
    .get<SyncConflict[]>('/integrations/hemis/conflicts/', { params })
    .then((r) => r.data);
};

export const resolveConflict = (id: string, data: ResolveConflictRequest) =>
  apiClient
    .post<SyncConflict>(`/integrations/hemis/${id}/resolve/`, data)
    .then((r) => r.data);

export const fetchSyncLogs = () =>
  apiClient
    .get<{ results: SyncLog[] } | SyncLog[]>('/integrations/logs/')
    .then((r) => (Array.isArray(r.data) ? r.data : (r.data as { results: SyncLog[] }).results));
