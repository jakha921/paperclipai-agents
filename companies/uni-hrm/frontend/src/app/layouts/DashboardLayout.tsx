import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  Users,
  Building2,
  Briefcase,
  GitFork,
  CalendarDays,
  CheckSquare,
  CalendarRange,
  ClipboardList,
  BarChart3,
  Clock,
  Wallet,
  CircleDollarSign,
  UserSearch,
  LogOut,
  GraduationCap,
  BookOpen,
  FileText,
  BarChart2,
  Download,
  PieChart,
  Link2,
  Settings,
} from 'lucide-react';
import { AppShell, Sidebar, type SidebarItem } from '@/shared/ui';
import { ToastContainer } from '@/shared/ui';
import { Avatar } from '@/shared/ui';
import { useAuthStore } from '@/store/auth';
import { NotificationBell } from '@/features/notifications/NotificationBell';
import { useNotificationSocket } from '@/features/notifications/useNotificationSocket';

export function DashboardLayout() {
  const { t } = useTranslation();
  const { user, logout } = useAuthStore();
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  useNotificationSocket(token);

  const navItems: SidebarItem[] = [
    { label: t('nav.dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { label: t('nav.employees'), href: '/employees', icon: Users },
    { label: t('nav.departments'), href: '/departments', icon: Building2 },
    { label: t('nav.positions'), href: '/positions', icon: Briefcase },
    { label: t('nav.orgChart'), href: '/org-chart', icon: GitFork },
    { label: t('nav.leaves'), href: '/leaves', icon: CalendarDays },
    { label: t('nav.leaveApproval'), href: '/leaves/approval', icon: CheckSquare },
    { label: t('nav.leaveCalendar'), href: '/leaves/calendar', icon: CalendarRange },
    { label: t('nav.attendance'), href: '/attendance', icon: ClipboardList },
    { label: t('nav.timesheet'), href: '/timesheet', icon: BarChart3 },
    { label: t('nav.schedules'), href: '/schedules', icon: Clock },
    { label: t('nav.payroll'), href: '/payroll', icon: Wallet },
    { label: t('nav.salaryConfig'), href: '/salary-config', icon: CircleDollarSign },
    { label: t('nav.recruitment'), href: '/recruitment/vacancies', icon: UserSearch },
    { label: t('nav.appraisal'), href: '/appraisals/cycles', icon: GraduationCap },
    { label: t('nav.training'), href: '/training/programs', icon: BookOpen },
    { label: t('nav.hrDashboard'), href: '/dashboard/hr', icon: BarChart2 },
    { label: t('nav.documents'), href: '/documents/templates', icon: FileText },
    { label: t('nav.reports'), href: '/reports', icon: Download },
    { label: t('nav.analytics'), href: '/analytics/turnover', icon: PieChart },
    { label: t('nav.hemis'), href: '/integrations/hemis', icon: Link2 },
    { label: t('nav.settings'), href: '/admin/settings', icon: Settings },
  ];

  return (
    <>
      <AppShell
        sidebar={
          <Sidebar
            items={navItems}
            header={
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-indigo-500 flex items-center justify-center text-white font-bold text-sm">
                  U
                </div>
                <span
                  className="text-lg font-bold text-white"
                  style={{ fontFamily: 'var(--font-heading)' }}
                >
                  Uni-HRM
                </span>
              </div>
            }
            footer={
              <div className="flex items-center gap-3">
                <Avatar name={user?.full_name ?? 'User'} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    {user?.full_name ?? 'User'}
                  </p>
                  <p className="text-xs text-indigo-300 truncate">{user?.email ?? ''}</p>
                </div>
                <div className="flex items-center gap-1">
                  <NotificationBell />
                  <button
                    onClick={logout}
                    className="text-indigo-300 hover:text-white transition-colors p-1"
                    title={t('auth.logout')}
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </div>
              </div>
            }
          />
        }
      >
        <Outlet />
      </AppShell>
      <ToastContainer />
    </>
  );
}
