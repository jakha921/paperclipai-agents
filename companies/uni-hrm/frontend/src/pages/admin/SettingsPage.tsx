import { useState, useEffect } from 'react';
import { Save, Mail, Clock, Calendar, Settings, Send } from 'lucide-react';
import { useSystemSettings, useUpdateSettings, useTestEmail } from '@/features/settings/api';
import type { UpdateSettingsData } from '@/features/settings/types';
import { toast } from '@/shared/ui';

const DAYS_OF_WEEK = [
  { value: 1, label: 'Пн' },
  { value: 2, label: 'Вт' },
  { value: 3, label: 'Ср' },
  { value: 4, label: 'Чт' },
  { value: 5, label: 'Пт' },
  { value: 6, label: 'Сб' },
  { value: 7, label: 'Вс' },
];

export default function SettingsPage() {
  const { data, isLoading } = useSystemSettings();
  const updateSettings = useUpdateSettings();
  const testEmailMutation = useTestEmail();

  const [formData, setFormData] = useState<UpdateSettingsData>({});
  const [testEmailAddress, setTestEmailAddress] = useState('');

  useEffect(() => {
    if (data) {
      setFormData({
        site_name: data.site_name,
        site_url: data.site_url,
        working_hours_start: data.working_hours_start,
        working_hours_end: data.working_hours_end,
        working_days: data.working_days,
        annual_leave_days: data.annual_leave_days,
        sick_leave_days: data.sick_leave_days,
        currency: data.currency,
        timezone: data.timezone,
        smtp_host: data.smtp_host,
        smtp_port: data.smtp_port,
        smtp_use_tls: data.smtp_use_tls,
        smtp_username: data.smtp_username,
        from_email: data.from_email,
      });
    }
  }, [data]);

  const handleChange = (field: keyof UpdateSettingsData, value: string | number | boolean | number[]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const toggleWorkingDay = (day: number) => {
    const days = (formData.working_days as number[]) ?? [];
    if (days.includes(day)) {
      handleChange(
        'working_days',
        days.filter((d) => d !== day),
      );
    } else {
      handleChange('working_days', [...days, day].sort());
    }
  };

  const handleSave = () => {
    updateSettings.mutate(formData, {
      onSuccess: () => toast('Настройки сохранены', 'success'),
      onError: () => toast('Ошибка сохранения настроек', 'error'),
    });
  };

  const handleTestEmail = () => {
    if (!testEmailAddress) return;
    testEmailMutation.mutate(
      { to_email: testEmailAddress },
      {
        onSuccess: (result) => {
          if (result.error) {
            toast(result.error, 'error');
          } else {
            toast(result.message ?? 'Тестовый email отправлен', 'success');
          }
        },
        onError: () => toast('Ошибка отправки тестового email', 'error'),
      },
    );
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 rounded w-64" />
          <div className="h-64 bg-slate-200 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings className="h-6 w-6 text-indigo-600" />
          <div>
            <h1
              className="text-2xl font-bold text-slate-900"
              style={{ fontFamily: 'var(--font-heading)' }}
            >
              Системные настройки
            </h1>
            <p className="text-sm text-slate-500">Конфигурация системы Uni-HRM</p>
          </div>
        </div>
        <button
          onClick={handleSave}
          disabled={updateSettings.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm font-medium"
        >
          <Save className="h-4 w-4" />
          {updateSettings.isPending ? 'Сохранение...' : 'Сохранить'}
        </button>
      </div>

      {/* Section 1: General */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <h2
          className="text-lg font-semibold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Общие настройки
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Название системы
            </label>
            <input
              type="text"
              value={(formData.site_name as string) ?? ''}
              onChange={(e) => handleChange('site_name', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">URL сайта</label>
            <input
              type="text"
              value={(formData.site_url as string) ?? ''}
              onChange={(e) => handleChange('site_url', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Валюта</label>
            <select
              value={(formData.currency as string) ?? 'UZS'}
              onChange={(e) => handleChange('currency', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="UZS">UZS -- Узбекский сум</option>
              <option value="USD">USD -- Доллар США</option>
              <option value="EUR">EUR -- Евро</option>
              <option value="RUB">RUB -- Российский рубль</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Часовой пояс</label>
            <select
              value={(formData.timezone as string) ?? 'Asia/Tashkent'}
              onChange={(e) => handleChange('timezone', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="Asia/Tashkent">Asia/Tashkent (UTC+5)</option>
              <option value="Europe/Moscow">Europe/Moscow (UTC+3)</option>
              <option value="UTC">UTC</option>
            </select>
          </div>
        </div>
      </div>

      {/* Section 2: Working Hours */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-indigo-600" />
          <h2
            className="text-lg font-semibold text-slate-900"
            style={{ fontFamily: 'var(--font-heading)' }}
          >
            Рабочее время
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Начало рабочего дня
            </label>
            <input
              type="time"
              value={((formData.working_hours_start as string) ?? '09:00').substring(0, 5)}
              onChange={(e) => handleChange('working_hours_start', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Конец рабочего дня
            </label>
            <input
              type="time"
              value={((formData.working_hours_end as string) ?? '18:00').substring(0, 5)}
              onChange={(e) => handleChange('working_hours_end', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Рабочие дни</label>
          <div className="flex gap-2 flex-wrap">
            {DAYS_OF_WEEK.map((day) => {
              const days = (formData.working_days as number[]) ?? [];
              const isActive = days.includes(day.value);
              return (
                <button
                  key={day.value}
                  type="button"
                  onClick={() => toggleWorkingDay(day.value)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {day.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Section 3: Leave Policies */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-indigo-600" />
          <h2
            className="text-lg font-semibold text-slate-900"
            style={{ fontFamily: 'var(--font-heading)' }}
          >
            Политики отпусков
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Дней ежегодного отпуска
            </label>
            <input
              type="number"
              min={0}
              max={365}
              value={(formData.annual_leave_days as number) ?? 28}
              onChange={(e) => handleChange('annual_leave_days', parseInt(e.target.value, 10))}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Дней больничного
            </label>
            <input
              type="number"
              min={0}
              max={365}
              value={(formData.sick_leave_days as number) ?? 14}
              onChange={(e) => handleChange('sick_leave_days', parseInt(e.target.value, 10))}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Section 4: Email (SMTP) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Mail className="h-5 w-5 text-indigo-600" />
          <h2
            className="text-lg font-semibold text-slate-900"
            style={{ fontFamily: 'var(--font-heading)' }}
          >
            Настройки Email (SMTP)
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">SMTP Хост</label>
            <input
              type="text"
              value={(formData.smtp_host as string) ?? ''}
              onChange={(e) => handleChange('smtp_host', e.target.value)}
              placeholder="smtp.gmail.com"
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">SMTP Порт</label>
            <input
              type="number"
              value={(formData.smtp_port as number) ?? 587}
              onChange={(e) => handleChange('smtp_port', parseInt(e.target.value, 10))}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              SMTP Пользователь
            </label>
            <input
              type="text"
              value={(formData.smtp_username as string) ?? ''}
              onChange={(e) => handleChange('smtp_username', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email отправителя
            </label>
            <input
              type="email"
              value={(formData.from_email as string) ?? ''}
              onChange={(e) => handleChange('from_email', e.target.value)}
              placeholder="noreply@uni-hrm.uz"
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="smtp_use_tls"
              checked={(formData.smtp_use_tls as boolean) ?? true}
              onChange={(e) => handleChange('smtp_use_tls', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            <label htmlFor="smtp_use_tls" className="text-sm font-medium text-slate-700">
              Использовать TLS
            </label>
          </div>
        </div>

        {/* Test Email */}
        <div className="border-t border-slate-100 pt-4">
          <p className="text-sm font-medium text-slate-700 mb-2">Тестовый Email</p>
          <div className="flex gap-3">
            <input
              type="email"
              value={testEmailAddress}
              onChange={(e) => setTestEmailAddress(e.target.value)}
              placeholder="your@email.com"
              className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={handleTestEmail}
              disabled={testEmailMutation.isPending || !testEmailAddress}
              className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 transition-colors text-sm font-medium"
            >
              <Send className="h-4 w-4" />
              {testEmailMutation.isPending ? 'Отправка...' : 'Отправить тест'}
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Save */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={updateSettings.isPending}
          className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm font-medium"
        >
          <Save className="h-4 w-4" />
          {updateSettings.isPending ? 'Сохранение...' : 'Сохранить настройки'}
        </button>
      </div>
    </div>
  );
}
