import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthLayout } from './layouts/AuthLayout';
import { DashboardLayout } from './layouts/DashboardLayout';
import { PrivateRoute } from './PrivateRoute';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { Skeleton } from '@/shared/ui';

const DashboardPage = lazy(() =>
  import('@/pages/DashboardPage').then((m) => ({ default: m.DashboardPage })),
);
const ProfilePage = lazy(() =>
  import('@/pages/ProfilePage').then((m) => ({ default: m.ProfilePage })),
);
const RolesPage = lazy(() =>
  import('@/pages/admin/RolesPage').then((m) => ({ default: m.RolesPage })),
);

const DepartmentsPage = lazy(() => import('@/pages/departments/DepartmentsPage'));
const PositionsPage = lazy(() => import('@/pages/positions/PositionsPage'));
const EmployeesListPage = lazy(() => import('@/pages/employees/EmployeesListPage'));
const CreateEmployeePage = lazy(() => import('@/pages/employees/CreateEmployeePage'));
const EditEmployeePage = lazy(() => import('@/pages/employees/EditEmployeePage'));
const EmployeeDetailPage = lazy(() => import('@/pages/employees/EmployeeDetailPage'));
const OrgChartPage = lazy(() => import('@/pages/org-chart/OrgChartPage'));
const MyLeavesPage = lazy(() => import('@/pages/leaves/MyLeavesPage'));
const LeaveApprovalPage = lazy(() => import('@/pages/leaves/LeaveApprovalPage'));
const LeaveCalendarPage = lazy(() => import('@/pages/leaves/LeaveCalendarPage'));
const AttendancePage = lazy(() => import('@/pages/attendance/AttendancePage'));
const TimesheetPage = lazy(() => import('@/pages/attendance/TimesheetPage'));
const SchedulesPage = lazy(() => import('@/pages/attendance/SchedulesPage'));
const PayrollPage = lazy(() => import('@/pages/payroll/PayrollPage'));
const PayslipPage = lazy(() => import('@/pages/payroll/PayslipPage'));
const SalaryConfigPage = lazy(() => import('@/pages/payroll/SalaryConfigPage'));
const VacanciesPage = lazy(() => import('@/pages/recruitment/VacanciesPage'));
const VacancyDetailPage = lazy(() => import('@/pages/recruitment/VacancyDetailPage'));
const CandidatesPage = lazy(() => import('@/pages/recruitment/CandidatesPage'));
const NotificationsPage = lazy(() => import('@/pages/notifications/NotificationsPage'));
const AppraisalCyclesPage = lazy(() => import('@/pages/appraisal/AppraisalCyclesPage'));
const KPIIndicatorsPage = lazy(() => import('@/pages/appraisal/KPIIndicatorsPage'));
const MyAppraisalPage = lazy(() => import('@/pages/appraisal/MyAppraisalPage'));
const ReviewPage = lazy(() => import('@/pages/appraisal/ReviewPage'));
const TrainingProgramsPage = lazy(() => import('@/pages/training/TrainingProgramsPage'));
const MyCoursesPage = lazy(() => import('@/pages/training/MyCoursesPage'));
const HRDashboardPage = lazy(() => import('@/pages/dashboard/HRDashboardPage'));
const DocumentTemplatesPage = lazy(() => import('@/pages/documents/DocumentTemplatesPage'));
const GenerateDocumentPage = lazy(() => import('@/pages/documents/GenerateDocumentPage'));
const MyDocumentsPage = lazy(() => import('@/pages/documents/MyDocumentsPage'));
const ReportsPage = lazy(() => import('@/pages/reports/ReportsPage'));
const TurnoverPage = lazy(() => import('@/pages/analytics/TurnoverPage'));
const DemographicsPage = lazy(() => import('@/pages/analytics/DemographicsPage'));
const DepartmentStatsPage = lazy(() => import('@/pages/analytics/DepartmentStatsPage'));
const AcademicLoadPage = lazy(() => import('@/pages/academic/AcademicLoadPage'));
const AcademicReferencesPage = lazy(() => import('@/pages/academic/AcademicReferencesPage'));
const ContestsPage = lazy(() => import('@/pages/academic/ContestsPage'));
const HEMISSyncPage = lazy(() => import('@/pages/integrations/HEMISSyncPage'));
const HEMISConflictsPage = lazy(() => import('@/pages/integrations/HEMISConflictsPage'));
const SettingsPage = lazy(() => import('@/pages/admin/SettingsPage'));

function PageLoader() {
  return (
    <div className="p-6 space-y-4">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        <Route element={<PrivateRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DashboardPage />
                </Suspense>
              }
            />
            <Route
              path="/profile"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ProfilePage />
                </Suspense>
              }
            />

            {/* Admin-only routes */}
            <Route element={<PrivateRoute requiredRole="super_admin" />}>
              <Route
                path="/admin/roles"
                element={
                  <Suspense fallback={<PageLoader />}>
                    <RolesPage />
                  </Suspense>
                }
              />
              <Route
                path="/admin/settings"
                element={
                  <Suspense fallback={<PageLoader />}>
                    <SettingsPage />
                  </Suspense>
                }
              />
            </Route>

            <Route
              path="/departments"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DepartmentsPage />
                </Suspense>
              }
            />
            <Route
              path="/positions"
              element={
                <Suspense fallback={<PageLoader />}>
                  <PositionsPage />
                </Suspense>
              }
            />
            <Route
              path="/employees"
              element={
                <Suspense fallback={<PageLoader />}>
                  <EmployeesListPage />
                </Suspense>
              }
            />
            <Route
              path="/employees/new"
              element={
                <Suspense fallback={<PageLoader />}>
                  <CreateEmployeePage />
                </Suspense>
              }
            />
            <Route
              path="/employees/:id/edit"
              element={
                <Suspense fallback={<PageLoader />}>
                  <EditEmployeePage />
                </Suspense>
              }
            />
            <Route
              path="/employees/:id"
              element={
                <Suspense fallback={<PageLoader />}>
                  <EmployeeDetailPage />
                </Suspense>
              }
            />
            <Route
              path="/org-chart"
              element={
                <Suspense fallback={<PageLoader />}>
                  <OrgChartPage />
                </Suspense>
              }
            />
            <Route
              path="/leaves"
              element={
                <Suspense fallback={<PageLoader />}>
                  <MyLeavesPage />
                </Suspense>
              }
            />
            <Route
              path="/leaves/approval"
              element={
                <Suspense fallback={<PageLoader />}>
                  <LeaveApprovalPage />
                </Suspense>
              }
            />
            <Route
              path="/leaves/calendar"
              element={
                <Suspense fallback={<PageLoader />}>
                  <LeaveCalendarPage />
                </Suspense>
              }
            />
            <Route
              path="/attendance"
              element={
                <Suspense fallback={<PageLoader />}>
                  <AttendancePage />
                </Suspense>
              }
            />
            <Route
              path="/timesheet"
              element={
                <Suspense fallback={<PageLoader />}>
                  <TimesheetPage />
                </Suspense>
              }
            />
            <Route
              path="/schedules"
              element={
                <Suspense fallback={<PageLoader />}>
                  <SchedulesPage />
                </Suspense>
              }
            />
            <Route
              path="/payroll"
              element={
                <Suspense fallback={<PageLoader />}>
                  <PayrollPage />
                </Suspense>
              }
            />
            <Route
              path="/payroll/:id"
              element={
                <Suspense fallback={<PageLoader />}>
                  <PayslipPage />
                </Suspense>
              }
            />
            <Route
              path="/salary-config"
              element={
                <Suspense fallback={<PageLoader />}>
                  <SalaryConfigPage />
                </Suspense>
              }
            />
            <Route path="/recruitment" element={<Navigate to="/recruitment/vacancies" replace />} />
            <Route
              path="/recruitment/vacancies"
              element={
                <Suspense fallback={<PageLoader />}>
                  <VacanciesPage />
                </Suspense>
              }
            />
            <Route
              path="/recruitment/vacancies/:id"
              element={
                <Suspense fallback={<PageLoader />}>
                  <VacancyDetailPage />
                </Suspense>
              }
            />
            <Route
              path="/recruitment/candidates"
              element={
                <Suspense fallback={<PageLoader />}>
                  <CandidatesPage />
                </Suspense>
              }
            />
            <Route
              path="/notifications"
              element={
                <Suspense fallback={<PageLoader />}>
                  <NotificationsPage />
                </Suspense>
              }
            />
            <Route path="/appraisals" element={<Navigate to="/appraisals/cycles" replace />} />
            <Route
              path="/appraisals/cycles"
              element={
                <Suspense fallback={<PageLoader />}>
                  <AppraisalCyclesPage />
                </Suspense>
              }
            />
            <Route
              path="/appraisals/kpis"
              element={
                <Suspense fallback={<PageLoader />}>
                  <KPIIndicatorsPage />
                </Suspense>
              }
            />
            <Route
              path="/appraisals/my"
              element={
                <Suspense fallback={<PageLoader />}>
                  <MyAppraisalPage />
                </Suspense>
              }
            />
            <Route
              path="/appraisals/review"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ReviewPage />
                </Suspense>
              }
            />
            <Route
              path="/training/programs"
              element={
                <Suspense fallback={<PageLoader />}>
                  <TrainingProgramsPage />
                </Suspense>
              }
            />
            <Route
              path="/training/my-courses"
              element={
                <Suspense fallback={<PageLoader />}>
                  <MyCoursesPage />
                </Suspense>
              }
            />
            <Route
              path="/dashboard/hr"
              element={
                <Suspense fallback={<PageLoader />}>
                  <HRDashboardPage />
                </Suspense>
              }
            />
            <Route
              path="/documents/templates"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DocumentTemplatesPage />
                </Suspense>
              }
            />
            <Route
              path="/documents/generate"
              element={
                <Suspense fallback={<PageLoader />}>
                  <GenerateDocumentPage />
                </Suspense>
              }
            />
            <Route
              path="/documents/my"
              element={
                <Suspense fallback={<PageLoader />}>
                  <MyDocumentsPage />
                </Suspense>
              }
            />
            <Route
              path="/reports"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ReportsPage />
                </Suspense>
              }
            />
            <Route
              path="/analytics/turnover"
              element={
                <Suspense fallback={<PageLoader />}>
                  <TurnoverPage />
                </Suspense>
              }
            />
            <Route
              path="/analytics/demographics"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DemographicsPage />
                </Suspense>
              }
            />
            <Route
              path="/analytics/departments"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DepartmentStatsPage />
                </Suspense>
              }
            />
            <Route
              path="/academic/load"
              element={
                <Suspense fallback={<PageLoader />}>
                  <AcademicLoadPage />
                </Suspense>
              }
            />
            <Route
              path="/academic/references"
              element={
                <Suspense fallback={<PageLoader />}>
                  <AcademicReferencesPage />
                </Suspense>
              }
            />
            <Route
              path="/academic/contests"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ContestsPage />
                </Suspense>
              }
            />
            <Route
              path="/integrations/hemis"
              element={
                <Suspense fallback={<PageLoader />}>
                  <HEMISSyncPage />
                </Suspense>
              }
            />
            <Route
              path="/integrations/hemis/conflicts"
              element={
                <Suspense fallback={<PageLoader />}>
                  <HEMISConflictsPage />
                </Suspense>
              }
            />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
