import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { PageHeader, Card, CardContent, Skeleton } from '@/shared/ui';
import { Users, Building2, CalendarDays, ClipboardList } from 'lucide-react';
import { apiClient } from '@/shared/lib/api-client';

function useEmployeesCount() {
  return useQuery({
    queryKey: ['dashboard', 'employees-count'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ count: number }>('/employees/', {
        params: { page_size: 1 },
      });
      return data.count;
    },
  });
}

function useDepartmentsCount() {
  return useQuery({
    queryKey: ['dashboard', 'departments-count'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ count: number }>('/departments/', {
        params: { page_size: 1 },
      });
      return data.count;
    },
  });
}

function usePendingLeavesCount() {
  return useQuery({
    queryKey: ['dashboard', 'pending-leaves'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ count: number }>('/leaves/requests/', {
        params: { status: 'PENDING', page_size: 1 },
      });
      return data.count;
    },
  });
}

function useTodayAttendanceCount() {
  const today = new Date().toISOString().split('T')[0];
  return useQuery({
    queryKey: ['dashboard', 'today-attendance', today],
    queryFn: async () => {
      const { data } = await apiClient.get<{ count: number }>('/attendance/records/', {
        params: { date: today, page_size: 1 },
      });
      return data.count;
    },
  });
}

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: number | undefined;
  isLoading: boolean;
  colorClass: string;
}

function StatCard({ icon: Icon, label, value, isLoading, colorClass }: StatCardProps) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4">
        <div className={`rounded-lg p-3 ${colorClass}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          {isLoading ? (
            <Skeleton className="h-8 w-16 mt-1" />
          ) : (
            <p className="text-2xl font-bold text-slate-900">{value ?? '—'}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const { t } = useTranslation();
  const employees = useEmployeesCount();
  const departments = useDepartmentsCount();
  const pendingLeaves = usePendingLeavesCount();
  const todayAttendance = useTodayAttendanceCount();

  return (
    <div>
      <PageHeader title={t('nav.dashboard')} description={t('app.subtitle')} />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          label={t('nav.employees')}
          value={employees.data}
          isLoading={employees.isLoading}
          colorClass="text-primary-600 bg-primary-50"
        />
        <StatCard
          icon={Building2}
          label={t('nav.departments')}
          value={departments.data}
          isLoading={departments.isLoading}
          colorClass="text-emerald-600 bg-emerald-50"
        />
        <StatCard
          icon={CalendarDays}
          label={t('nav.leaveApproval')}
          value={pendingLeaves.data}
          isLoading={pendingLeaves.isLoading}
          colorClass="text-amber-600 bg-amber-50"
        />
        <StatCard
          icon={ClipboardList}
          label={t('nav.attendance')}
          value={todayAttendance.data}
          isLoading={todayAttendance.isLoading}
          colorClass="text-blue-600 bg-blue-50"
        />
      </div>
    </div>
  );
}
