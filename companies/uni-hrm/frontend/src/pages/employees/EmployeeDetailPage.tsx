import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, FileText, History } from 'lucide-react';
import { useEmployee } from '../../features/employees/api';
import { Button, Card, CardHeader, CardContent, Skeleton } from '../../shared/ui';
import {
  EMPLOYEE_STATUS_LABELS,
  EMPLOYEE_STATUS_COLORS,
  EMPLOYMENT_HISTORY_LABELS,
} from '../../shared/constants/statuses';

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-800 font-medium">{value}</span>
    </div>
  );
}

export default function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: employee, isLoading } = useEmployee(id ?? '');
  const [activeTab, setActiveTab] = useState<'main' | 'docs' | 'history'>('main');

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="p-6">
        <Button variant="secondary" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Назад
        </Button>
        <p className="mt-4 text-slate-500">Сотрудник не найден</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="secondary" onClick={() => navigate('/employees')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> К списку
        </Button>
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          {employee.full_name}
        </h1>
        <span
          className={`text-sm px-3 py-1 rounded-full font-medium ${EMPLOYEE_STATUS_COLORS[employee.status]}`}
        >
          {EMPLOYEE_STATUS_LABELS[employee.status]}
        </span>
      </div>

      <div className="flex items-center gap-6 p-6 bg-white rounded-xl border border-slate-200">
        <div className="h-20 w-20 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 text-2xl font-bold flex-shrink-0">
          {employee.last_name?.[0]}
          {employee.first_name?.[0]}
        </div>
        <div className="flex-1">
          <h2 className="text-xl font-semibold text-slate-900">{employee.full_name}</h2>
          <p className="text-slate-500">
            {employee.position_name} · {employee.department_name}
          </p>
          <p className="text-sm text-slate-400 mt-1">Табельный: {employee.employee_number}</p>
        </div>
        <Button onClick={() => navigate(`/employees/${id}/edit`)}>Редактировать</Button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-0">
          {(
            [
              { key: 'main', label: 'Основное', icon: User },
              { key: 'docs', label: 'Документы', icon: FileText },
              { key: 'history', label: 'История', icon: History },
            ] as const
          ).map(({ key, label, icon: Icon }) => (
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

      {activeTab === 'main' && (
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <h3 className="font-semibold text-slate-900">Личные данные</h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoRow label="Дата рождения" value={employee.birth_date} />
              <InfoRow
                label="Пол"
                value={employee.gender === 'MALE' ? 'Мужской' : 'Женский'}
              />
              <InfoRow label="Национальность" value={employee.nationality} />
              <InfoRow label="Дата найма" value={employee.hire_date} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <h3 className="font-semibold text-slate-900">Контакты</h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoRow label="Телефон" value={employee.phone} />
              <InfoRow label="Email" value={employee.email || '—'} />
              <InfoRow label="Адрес" value={employee.address || '—'} />
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'docs' && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Документы</h3>
          </CardHeader>
          <CardContent className="space-y-3">
            <InfoRow label="ПИНФЛ" value={employee.pinfl} />
            <InfoRow label="ИНН" value={employee.inn || '—'} />
            <InfoRow label="Паспорт" value={employee.passport_series} />
          </CardContent>
        </Card>
      )}

      {activeTab === 'history' && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">История занятости</h3>
          </CardHeader>
          <CardContent>
            {!employee.history || employee.history.length === 0 ? (
              <p className="text-sm text-slate-400">История пуста</p>
            ) : (
              <div className="relative pl-4 border-l-2 border-indigo-100 space-y-4">
                {employee.history.map((h) => (
                  <div key={h.id} className="relative">
                    <div className="absolute -left-[21px] top-1 h-3 w-3 rounded-full bg-indigo-500" />
                    <div className="bg-slate-50 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-slate-800">
                          {EMPLOYMENT_HISTORY_LABELS[h.change_reason]}
                        </span>
                        <span className="text-xs text-slate-400">{h.start_date}</span>
                      </div>
                      <p className="text-sm text-slate-600 mt-1">
                        {h.position_name} · {h.department_name}
                      </p>
                      {h.order_number && (
                        <p className="text-xs text-slate-400 mt-1">
                          Приказ №{h.order_number} от {h.order_date}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
