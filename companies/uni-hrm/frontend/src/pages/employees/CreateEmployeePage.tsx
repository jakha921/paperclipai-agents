import { useState } from 'react';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCreateEmployee } from '../../features/employees/api';
import { useDepartments, usePositions } from '../../features/departments/api';
import type { CreateEmployeeData } from '../../features/employees/types';
import { Button, Card, CardHeader, CardContent, Input } from '../../shared/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const step1Schema = z.object({
  last_name: z.string().min(1, 'Обязательное поле'),
  first_name: z.string().min(1, 'Обязательное поле'),
  middle_name: z.string(),
  birth_date: z.string().min(1, 'Обязательное поле'),
  gender: z.enum(['MALE', 'FEMALE']),
  nationality: z.string().min(1, 'Обязательное поле'),
  pinfl: z.string().length(14, 'ПИНФЛ — 14 цифр'),
  inn: z.string().optional(),
  passport_series: z.string().min(1, 'Обязательное поле'),
});

const step2Schema = z.object({
  department: z.string().min(1, 'Выберите подразделение'),
  position: z.string().min(1, 'Выберите должность'),
  hire_date: z.string().min(1, 'Обязательное поле'),
  contract_type: z.enum(['PERMANENT', 'PART_TIME', 'HOURLY']),
});

const step4Schema = z.object({
  phone: z.string().min(1, 'Обязательное поле'),
  email: z.string().email().optional().or(z.literal('')),
  address: z.string(),
});

type Step1Data = z.infer<typeof step1Schema>;
type Step2Data = z.infer<typeof step2Schema>;
type Step4Data = z.infer<typeof step4Schema>;

const STEPS = [
  { label: 'Личные данные', desc: 'ФИО, ПИНФЛ, дата рождения' },
  { label: 'Должность', desc: 'Подразделение, должность, контракт' },
  { label: 'Документы', desc: 'Фото и сканы' },
  { label: 'Контакты', desc: 'Телефон, email, адрес' },
];

export default function CreateEmployeePage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [step1Data, setStep1Data] = useState<Step1Data | null>(null);
  const [step2Data, setStep2Data] = useState<Step2Data | null>(null);
  const createEmployee = useCreateEmployee();
  const { data: depts } = useDepartments();
  const { data: positions } = usePositions();

  const form1 = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    defaultValues: { gender: 'MALE', nationality: 'Узбек', middle_name: '' },
  });
  const form2 = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
    defaultValues: { contract_type: 'PERMANENT' },
  });
  const form4 = useForm<Step4Data>({
    resolver: zodResolver(step4Schema),
    defaultValues: { email: '', address: '' },
  });

  const onStep1 = (data: Step1Data) => {
    setStep1Data(data);
    setStep(1);
  };
  const onStep2 = (data: Step2Data) => {
    setStep2Data(data);
    setStep(2);
  };

  const onFinish = async (data: Step4Data) => {
    if (!step1Data || !step2Data) return;
    const payload: CreateEmployeeData = {
      ...step1Data,
      ...step2Data,
      ...data,
    };
    await createEmployee.mutateAsync(payload);
    navigate('/employees');
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="secondary" onClick={() => navigate('/employees')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Назад
        </Button>
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Новый сотрудник
        </h1>
      </div>

      {/* Stepper */}
      <div className="flex items-center gap-0">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center flex-1">
            <div className="flex flex-col items-center">
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  i < step
                    ? 'bg-indigo-600 text-white'
                    : i === step
                      ? 'bg-indigo-600 text-white ring-4 ring-indigo-100'
                      : 'bg-slate-100 text-slate-400'
                }`}
              >
                {i < step ? <Check className="h-4 w-4" /> : i + 1}
              </div>
              <span className="text-xs text-slate-500 mt-1 text-center">{s.label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className={`flex-1 h-0.5 mx-2 mb-4 ${i < step ? 'bg-indigo-600' : 'bg-slate-200'}`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Личные данные */}
      {step === 0 && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Личные данные</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={form1.handleSubmit(onStep1)} className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-sm font-medium text-slate-700">Фамилия *</label>
                  <Input {...form1.register('last_name')} className="mt-1" />
                  {form1.formState.errors.last_name && (
                    <p className="text-xs text-red-500 mt-1">
                      {form1.formState.errors.last_name.message}
                    </p>
                  )}
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Имя *</label>
                  <Input {...form1.register('first_name')} className="mt-1" />
                  {form1.formState.errors.first_name && (
                    <p className="text-xs text-red-500 mt-1">
                      {form1.formState.errors.first_name.message}
                    </p>
                  )}
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Отчество</label>
                  <Input {...form1.register('middle_name')} className="mt-1" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-700">Дата рождения *</label>
                  <Input {...form1.register('birth_date')} type="date" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Пол *</label>
                  <select
                    {...form1.register('gender')}
                    className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  >
                    <option value="MALE">Мужской</option>
                    <option value="FEMALE">Женский</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Национальность *</label>
                <Input
                  {...form1.register('nationality')}
                  className="mt-1"
                  placeholder="Узбек"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-700">
                    ПИНФЛ * (14 цифр)
                  </label>
                  <Input {...form1.register('pinfl')} maxLength={14} className="mt-1" />
                  {form1.formState.errors.pinfl && (
                    <p className="text-xs text-red-500 mt-1">
                      {form1.formState.errors.pinfl.message}
                    </p>
                  )}
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">ИНН (9 цифр)</label>
                  <Input {...form1.register('inn')} maxLength={9} className="mt-1" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Серия паспорта *</label>
                <Input
                  {...form1.register('passport_series')}
                  placeholder="AA1234567"
                  className="mt-1"
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit">
                  Далее <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Должность */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Должность и подразделение</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={form2.handleSubmit(onStep2)} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Подразделение *</label>
                <select
                  {...form2.register('department')}
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                >
                  <option value="">Выберите подразделение</option>
                  {depts?.results?.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name_display || d.name?.ru}
                    </option>
                  ))}
                </select>
                {form2.formState.errors.department && (
                  <p className="text-xs text-red-500 mt-1">
                    {form2.formState.errors.department.message}
                  </p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Должность *</label>
                <select
                  {...form2.register('position')}
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                >
                  <option value="">Выберите должность</option>
                  {positions?.results?.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name?.ru || p.code}
                    </option>
                  ))}
                </select>
                {form2.formState.errors.position && (
                  <p className="text-xs text-red-500 mt-1">
                    {form2.formState.errors.position.message}
                  </p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-700">Дата найма *</label>
                  <Input {...form2.register('hire_date')} type="date" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Тип договора *</label>
                  <select
                    {...form2.register('contract_type')}
                    className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  >
                    <option value="PERMANENT">Основное место работы</option>
                    <option value="PART_TIME">Совместительство</option>
                    <option value="HOURLY">Почасовая оплата</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-between">
                <Button type="button" variant="secondary" onClick={() => setStep(0)}>
                  <ArrowLeft className="h-4 w-4 mr-2" /> Назад
                </Button>
                <Button type="submit">
                  Далее <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Документы */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Документы и фото</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-slate-500">
                Загрузка фото и документов (опционально)
              </p>
              <div className="border-2 border-dashed border-slate-200 rounded-lg p-8 text-center">
                <p className="text-sm text-slate-400">Drag & Drop фото сотрудника</p>
                <p className="text-xs text-slate-300 mt-1">PNG, JPG до 5MB</p>
              </div>
            </div>
            <div className="flex justify-between mt-4">
              <Button type="button" variant="secondary" onClick={() => setStep(1)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Назад
              </Button>
              <Button type="button" onClick={() => setStep(3)}>
                Далее <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Контакты */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-slate-900">Контактная информация</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={form4.handleSubmit(onFinish)} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700">
                  Телефон * (+998XXXXXXXXX)
                </label>
                <Input
                  {...form4.register('phone')}
                  placeholder="+998901234567"
                  className="mt-1"
                />
                {form4.formState.errors.phone && (
                  <p className="text-xs text-red-500 mt-1">
                    {form4.formState.errors.phone.message}
                  </p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Email</label>
                <Input {...form4.register('email')} type="email" className="mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Адрес</label>
                <textarea
                  {...form4.register('address')}
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm resize-none h-20"
                  placeholder="г. Ташкент, ул. ..."
                />
              </div>
              <div className="flex justify-between">
                <Button type="button" variant="secondary" onClick={() => setStep(2)}>
                  <ArrowLeft className="h-4 w-4 mr-2" /> Назад
                </Button>
                <Button type="submit" disabled={createEmployee.isPending}>
                  {createEmployee.isPending ? (
                    'Создание...'
                  ) : (
                    <>
                      <Check className="h-4 w-4 mr-2" /> Создать сотрудника
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
