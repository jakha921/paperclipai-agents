import { useState, useEffect } from 'react';
import { fetchPositions } from './api';
import type { Position } from './types';

export function usePositions() {
  const [data, setData] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPositions()
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Error'))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}
