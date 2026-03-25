import { useEffect } from 'react';
import { ArrowLeft, Save } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import { useEmployee, useUpdateEmployee } from '../../features/employees/api';
import { useDepartments, usePositions } from '../../features/departments/api';
import { Button, Card, CardHeader, CardContent, Input, Skeleton } from '../../shared/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const editSchema = z.object({
  last_name: z.string().min(1, 'Обязательное поле'),
  first_name: z.string().min(1, 'Обязательное поле'),
  middle_name: z.string(),
  birth_date: z.string().min(1, 'Обязательное поле'),
  gender: z.enum(['MALE', 'FEMALE']),
  nationality: z.string().min(1, 'Обязательное поле'),
  pinfl: z.string().length(14, 'ПИНФЛ — 14 цифр'),
  inn: z.string().optional(),
  passport_series: z.string().min(1, 'Обязательное поле'),
  department: z.string().min(1, 'Выберите подразделение'),
  position: z.string().min(1, 'Выберите должность'),
  hire_date: z.string().min(1, 'Обязательное поле'),
  contract_type: z.enum(['PERMANENT', 'PART_TIME', 'HOURLY']),
  phone: z.string().min(1, 'Обязательное поле'),
  email: z.string().email().optional().or(z.literal('')),
  address: z.string(),
});

type EditFormData = z.infer<typeof editSchema>;

export default function EditEmployeePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: employee, isLoading: isLoadingEmployee } = useEmployee(id ?? '');
  const updateEmployee = useUpdateEmployee();
  const { data: depts } = useDepartments();
  const { data: positions } = usePositions();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EditFormData>({
    resolver: zodResolver(editSchema),
  });

  useEffect(() => {
    if (employee) {
      reset({
        last_name: employee.last_name,
        first_name: employee.first_name,
        middle_name: employee.middle_name ?? '',
        birth_date: employee.birth_date,
        gender: employee.gender,
        nationality: employee.nationality,
        pinfl: employee.pinfl,
        inn: employee.inn ?? '',
        passport_series: employee.passport_series,
        department: String(
          typeof employee.department === 'object' ? employee.department.id : employee.department,
        ),
        position: String(
          typeof employee.position === 'object' ? employee.position.id : employee.position,
        ),
        hire_date: employee.hire_date,
        contract_type: employee.contract_type,
        phone: employee.phone,
        email: employee.email ?? '',
        address: employee.address ?? '',
      });
    }
  }, [employee, reset]);

  const onSubmit = async (data: EditFormData) => {
    if (!id) return;
    await updateEmployee.mutateAsync({ id, data });
    navigate(`/employees/${id}`);
  };

  if (isLoadingEmployee) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="p-6">
        <Button variant="secondary" onClick={() => navigate('/employees')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Назад
        </Button>
        <p className="mt-4 text-slate-500">Сотрудник не найден</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="secondary" onClick={() => navigate(`/employees/${id}`)}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Назад
        </Button>
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Редактировать: {employee.full_name}
        </h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Личные данные</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Фамилия *</label>
                <Input {...register('last_name')} className="mt-1" />
                {errors.last_name && (
                  <p className="text-xs text-red-500 mt-1">{errors.last_name.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Имя *</label>
                <Input {...register('first_name')} className="mt-1" />
                {errors.first_name && (
                  <p className="text-xs text-red-500 mt-1">{errors.first_name.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Отчество</label>
                <Input {...register('middle_name')} className="mt-1" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Дата рождения *</label>
                <Input {...register('birth_date')} type="date" className="mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Пол *</label>
                <select
                  {...register('gender')}
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                >
                  <option value="MALE">Мужской</option>
                  <option value="FEMALE">Женский</option>
                </select>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Национальность *</label>
              <Input {...register('nationality')} className="mt-1" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-700">ПИНФЛ * (14 цифр)</label>
                <Input {...register('pinfl')} maxLength={14} className="mt-1" />
                {errors.pinfl && (
                  <p className="text-xs text-red-500 mt-1">{errors.pinfl.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">ИНН (9 цифр)</label>
                <Input {...register('inn')} maxLength={9} className="mt-1" />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Серия паспорта *</label>
              <Input {...register('passport_series')} className="mt-1" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Должность и подразделение</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Подразделение *</label>
              <select
                {...register('department')}
                className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              >
                <option value="">Выберите подразделение</option>
                {depts?.results?.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name_display || d.name?.ru}
                  </option>
                ))}
              </select>
              {errors.department && (
                <p className="text-xs text-red-500 mt-1">{errors.department.message}</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Должность *</label>
              <select
                {...register('position')}
                className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              >
                <option value="">Выберите должность</option>
                {positions?.results?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name?.ru || p.code}
                  </option>
                ))}
              </select>
              {errors.position && (
                <p className="text-xs text-red-500 mt-1">{errors.position.message}</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Дата найма *</label>
                <Input {...register('hire_date')} type="date" className="mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Тип договора *</label>
                <select
                  {...register('contract_type')}
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                >
                  <option value="PERMANENT">Основное место работы</option>
                  <option value="PART_TIME">Совместительство</option>
                  <option value="HOURLY">Почасовая оплата</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Контактная информация</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">
                Телефон * (+998XXXXXXXXX)
              </label>
              <Input {...register('phone')} placeholder="+998901234567" className="mt-1" />
              {errors.phone && (
                <p className="text-xs text-red-500 mt-1">{errors.phone.message}</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Email</label>
              <Input {...register('email')} type="email" className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Адрес</label>
              <textarea
                {...register('address')}
                className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm resize-none h-20"
                placeholder="г. Ташкент, ул. ..."
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={() => navigate(`/employees/${id}`)}>
            Отмена
          </Button>
          <Button type="submit" disabled={updateEmployee.isPending}>
            {updateEmployee.isPending ? (
              'Сохранение...'
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" /> Сохранить изменения
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
