import { useState } from 'react';
import { BookOpen, Award, GraduationCap } from 'lucide-react';
import { useAcademicDegrees, useAcademicTitles, useSubjects } from '@/features/academic';
import { useTranslation } from 'react-i18next';

type Tab = 'degrees' | 'titles' | 'subjects';

function getLocalizedName(name: Record<string, string>, lang: string): string {
  return name[lang] ?? name.ru ?? name.en ?? '';
}

export default function AcademicReferencesPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [activeTab, setActiveTab] = useState<Tab>('degrees');

  const { data: degreesData, isLoading: degreesLoading } = useAcademicDegrees();
  const { data: titlesData, isLoading: titlesLoading } = useAcademicTitles();
  const { data: subjectsData, isLoading: subjectsLoading } = useSubjects();

  const degrees = degreesData?.results ?? [];
  const titles = titlesData?.results ?? [];
  const subjects = subjectsData?.results ?? [];

  const tabs = [
    { key: 'degrees' as Tab, label: t('academic.degrees'), icon: GraduationCap },
    { key: 'titles' as Tab, label: t('academic.titles'), icon: Award },
    { key: 'subjects' as Tab, label: t('academic.subjects'), icon: BookOpen },
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'var(--font-heading)' }}>
          {t('academic.references')}
        </h1>
        <p className="text-sm text-slate-500 mt-1">{t('academic.referencesDescription')}</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-0">
          {tabs.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === key
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Degrees Tab */}
      {activeTab === 'degrees' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {degreesLoading ? (
            <LoadingSkeleton />
          ) : degrees.length === 0 ? (
            <EmptyBlock icon={GraduationCap} text={t('academic.noDegrees')} />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.name')}</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.code')}</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.country')}</th>
                </tr>
              </thead>
              <tbody>
                {degrees.map((d) => (
                  <tr key={d.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900">{getLocalizedName(d.name, lang)}</td>
                    <td className="px-4 py-3 text-slate-600">{d.code}</td>
                    <td className="px-4 py-3 text-slate-600">{d.country}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Titles Tab */}
      {activeTab === 'titles' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {titlesLoading ? (
            <LoadingSkeleton />
          ) : titles.length === 0 ? (
            <EmptyBlock icon={Award} text={t('academic.noTitles')} />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.name')}</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.code')}</th>
                </tr>
              </thead>
              <tbody>
                {titles.map((tl) => (
                  <tr key={tl.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900">{getLocalizedName(tl.name, lang)}</td>
                    <td className="px-4 py-3 text-slate-600">{tl.code}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Subjects Tab */}
      {activeTab === 'subjects' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {subjectsLoading ? (
            <LoadingSkeleton />
          ) : subjects.length === 0 ? (
            <EmptyBlock icon={BookOpen} text={t('academic.noSubjects')} />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.name')}</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.code')}</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.credits')}</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.status')}</th>
                </tr>
              </thead>
              <tbody>
                {subjects.map((s) => (
                  <tr key={s.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900">{getLocalizedName(s.name, lang)}</td>
                    <td className="px-4 py-3 text-slate-600">{s.code}</td>
                    <td className="px-4 py-3 text-slate-600">{s.credits}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          s.is_active
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {s.is_active ? t('academic.active') : t('academic.inactive')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="p-6 space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-10 bg-slate-200 animate-pulse rounded-lg" />
      ))}
    </div>
  );
}

function EmptyBlock({ icon: Icon, text }: { icon: React.ComponentType<{ className?: string }>; text: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <Icon className="h-12 w-12 mb-3" />
      <p className="text-sm font-medium">{text}</p>
    </div>
  );
}
