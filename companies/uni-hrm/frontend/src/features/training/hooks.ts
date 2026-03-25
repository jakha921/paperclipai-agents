import { useState, useEffect, useCallback } from 'react';
import { fetchPrograms, fetchMyEnrollments, enrollCourse } from './api';
import type { TrainingProgram, Enrollment, EnrollCourseRequest } from './types';

export function useTrainingPrograms() {
  const [data, setData] = useState<TrainingProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPrograms()
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Error'))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export function useMyEnrollments() {
  const [data, setData] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMyEnrollments()
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Error'))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export function useEnrollCourse() {
  const [loading, setLoading] = useState(false);

  const enroll = useCallback(async (req: EnrollCourseRequest): Promise<Enrollment | null> => {
    setLoading(true);
    try {
      return await enrollCourse(req);
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { enroll, loading };
}
