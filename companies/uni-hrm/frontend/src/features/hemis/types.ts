export interface HEMISMapping {
  id: string;
  content_type: 'department' | 'employee' | 'subject';
  local_id: string;
  hemis_id: string;
  last_synced_at: string | null;
  sync_status: 'success' | 'error' | 'pending';
}

export interface SyncStats {
  created: number;
  updated: number;
  errors: number;
}

export interface SyncLog {
  id: string;
  sync_type: 'departments' | 'employees' | 'academic' | 'full';
  started_at: string;
  completed_at: string | null;
  status: 'running' | 'success' | 'error';
  stats: SyncStats | Record<string, SyncStats>;
  error_message: string;
}

export interface SyncConflict {
  id: string;
  mapping: HEMISMapping;
  field_name: string;
  local_value: string;
  hemis_value: string;
  is_resolved: boolean;
  resolution: 'local' | 'hemis' | '';
  resolved_by: string | null;
  resolved_by_name: string | null;
}

export interface SyncRequest {
  sync_type: 'departments' | 'employees' | 'full';
}

export interface ResolveConflictRequest {
  resolution: 'local' | 'hemis';
}
