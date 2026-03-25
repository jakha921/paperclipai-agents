import { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { Skeleton } from '@/shared/ui';

interface PrivateRouteProps {
  requiredRole?: string;
}

export function PrivateRoute({ requiredRole }: PrivateRouteProps = {}) {
  const { isAuthenticated, isLoading, user, fetchMe, hasRole } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchMe();
    }
  }, [isAuthenticated, user, fetchMe]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="w-64 space-y-4">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>
    );
  }

  if (requiredRole && user && !hasRole(requiredRole) && !user.roles?.includes('super_admin')) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
