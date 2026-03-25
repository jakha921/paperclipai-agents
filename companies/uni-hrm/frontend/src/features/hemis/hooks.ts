import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from './api';
import type { SyncRequest, ResolveConflictRequest } from './types';

export const useSyncLogs = () =>
  useQuery({ queryKey: ['sync-logs'], queryFn: api.fetchSyncLogs });

export const useHEMISStatus = () =>
  useQuery({
    queryKey: ['hemis-status'],
    queryFn: api.fetchHEMISStatus,
    refetchInterval: 10000,
  });

export const useSyncConflicts = (resolved?: boolean | null) =>
  useQuery({
    queryKey: ['sync-conflicts', resolved],
    queryFn: () => api.fetchSyncConflicts(resolved),
  });

export const useRunSync = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SyncRequest) => api.runSync(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['hemis-status'] });
      qc.invalidateQueries({ queryKey: ['sync-logs'] });
    },
  });
};

export const useResolveConflict = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ResolveConflictRequest }) =>
      api.resolveConflict(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sync-conflicts'] }),
  });
};
