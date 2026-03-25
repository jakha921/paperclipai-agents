import type { Position } from './types';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchPositions(): Promise<Position[]> {
  const res = await fetch(`${API_BASE}/api/v1/positions/`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch positions');
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}
