import { useState } from 'react';
import { AlertTriangle, BookOpen } from 'lucide-react';
import { useAcademicLoads } from '@/features/academic';
import type { LoadType } from '@/features/academic';
import { useDepartments } from '@/features/departments';
import { LOAD_TYPE_LABELS } from '@/shared/constants/statuses';
import { useTranslation } from 'react-i18next';

const CURRENT_YEAR = `${new Date().getFullYear()}-${new Date().getFullYear() + 1}`;
const ACADEMIC_YEARS = [
  `${new Date().getFullYear()}-${new Date().getFullYear() + 1}`,
  `${new Date().getFullYear() - 1}-${new Date().getFullYear()}`,
  `${new Date().getFullYear() - 2}-${new Date().getFullYear() - 1}`,
];

const MAX_HOURS = 900;

function getLocalizedName(name: Record<string, string> | string, lang: string): string {
  if (typeof name === 'string') return name;
  return name[lang] ?? name.ru ?? name.en ?? '';
}

export default function AcademicLoadPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [academicYear, setAcademicYear] = useState(CURRENT_YEAR);
  const [semester, setSemester] = useState<string>('');
  const [departmentId, setDepartmentId] = useState<string>('');

  const params: Record<string, string> = { academic_year: academicYear };
  if (semester) params.semester = semester;
  if (departmentId) params.department = departmentId;

  const { data, isLoading } = useAcademicLoads(params);
  const { data: depsData } = useDepartments();

  const loads = data?.results ?? [];
  const departments = depsData?.results ?? [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'var(--font-heading)' }}>
          {t('academic.load')}
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          {t('academic.loadDescription')}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">{t('academic.academicYear')}</label>
          <select
            value={academicYear}
            onChange={(e) => setAcademicYear(e.target.value)}
            className="border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {ACADEMIC_YEARS.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">{t('academic.semester')}</label>
          <select
            value={semester}
            onChange={(e) => setSemester(e.target.value)}
            className="border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">{t('academic.allSemesters')}</option>
            <option value="1">1</option>
            <option value="2">2</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">{t('academic.department')}</label>
          <select
            value={departmentId}
            onChange={(e) => setDepartmentId(e.target.value)}
            className="border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">{t('academic.allDepartments')}</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {getLocalizedName(d.name, lang)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-slate-200 animate-pulse rounded-lg" />
            ))}
          </div>
        ) : loads.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <BookOpen className="h-12 w-12 mb-3" />
            <p className="text-sm font-medium">{t('academic.noLoads')}</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.employee')}</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.subject')}</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.semester')}</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">{t('academic.lectures')}</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">{t('academic.seminars')}</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">{t('academic.labs')}</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">{t('academic.totalHours')}</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.type')}</th>
              </tr>
            </thead>
            <tbody>
              {loads.map((load) => (
                <tr key={load.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-900">{load.employee}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {load.subject_detail
                      ? getLocalizedName(load.subject_detail.name, lang)
                      : load.subject}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{load.semester}</td>
                  <td className="px-4 py-3 text-right text-slate-600">{load.lecture_hours}</td>
                  <td className="px-4 py-3 text-right text-slate-600">{load.seminar_hours}</td>
                  <td className="px-4 py-3 text-right text-slate-600">{load.lab_hours}</td>
                  <td className="px-4 py-3 text-right">
                    <span className={load.total_hours > MAX_HOURS ? 'text-red-600 font-semibold' : 'text-slate-900 font-medium'}>
                      {load.total_hours}
                    </span>
                    {load.total_hours > MAX_HOURS && (
                      <AlertTriangle className="inline-block ml-1 h-4 w-4 text-red-500" />
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      load.load_type === 'PRIMARY'
                        ? 'bg-indigo-100 text-indigo-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {LOAD_TYPE_LABELS[load.load_type as LoadType] ?? load.load_type}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
