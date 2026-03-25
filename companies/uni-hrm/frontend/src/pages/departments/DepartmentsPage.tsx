import { useState } from 'react';
import { Building2, Plus, ChevronRight } from 'lucide-react';
import {
  useDepartmentTree,
  useCreateDepartment,
} from '../../features/departments/api';
import type { Department, CreateDepartmentData } from '../../features/departments/types';
import {
  Button,
  Card,
  CardHeader,
  CardContent,
  Modal,
  Input,
  PageHeader,
  EmptyState,
  Skeleton,
} from '../../shared/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const departmentSchema = z.object({
  code: z.string().min(1, 'Введите код'),
  name_ru: z.string().min(1, 'Введите название'),
  name_uz: z.string(),
  name_en: z.string(),
  department_type: z.enum(['RECTORATE', 'FACULTY', 'DEPARTMENT', 'ADMIN_SERVICE', 'SUPPORT_UNIT']),
  is_active: z.boolean(),
  parent: z.string().nullable().optional(),
});

type DepartmentFormData = z.infer<typeof departmentSchema>;

const DEPT_TYPE_LABELS: Record<string, string> = {
  RECTORATE: 'Ректорат',
  FACULTY: 'Факультет',
  DEPARTMENT: 'Кафедра',
  ADMIN_SERVICE: 'Администр. служба',
  SUPPORT_UNIT: 'Вспомогательная',
};

const DEPT_TYPE_COLORS: Record<string, string> = {
  RECTORATE: 'bg-purple-100 text-purple-700',
  FACULTY: 'bg-blue-100 text-blue-700',
  DEPARTMENT: 'bg-green-100 text-green-700',
  ADMIN_SERVICE: 'bg-amber-100 text-amber-700',
  SUPPORT_UNIT: 'bg-slate-100 text-slate-700',
};

function DepartmentNode({ dept, level = 0 }: { dept: Department; level?: number }) {
  const [expanded, setExpanded] = useState(level < 2);
  const hasChildren = dept.children && dept.children.length > 0;

  return (
    <div>
      <div
        className="flex items-center gap-2 py-2 px-3 hover:bg-slate-50 rounded-lg group cursor-pointer"
        style={{ paddingLeft: `${(level + 1) * 16}px` }}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren ? (
          <ChevronRight
            className={`h-4 w-4 text-slate-400 transition-transform ${expanded ? 'rotate-90' : ''}`}
          />
        ) : (
          <span className="w-4" />
        )}
        <Building2 className="h-4 w-4 text-indigo-500 flex-shrink-0" />
        <span className="text-sm font-medium text-slate-800 flex-1">
          {dept.name_display || dept.name?.ru || dept.code}
        </span>
        <span className="text-xs text-slate-400">{dept.code}</span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${DEPT_TYPE_COLORS[dept.department_type]}`}
        >
          {DEPT_TYPE_LABELS[dept.department_type]}
        </span>
        <span className="text-xs text-slate-500 min-w-[40px] text-right">
          {dept.employee_count} чел.
        </span>
        {!dept.is_active && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600">
            Неактивно
          </span>
        )}
      </div>
      {expanded && hasChildren && (
        <div>
          {dept.children!.map((child) => (
            <DepartmentNode key={child.id} dept={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function countDepartments(dept: Department): number {
  return 1 + (dept.children?.reduce((s, c) => s + countDepartments(c), 0) ?? 0);
}

export default function DepartmentsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { data: tree, isLoading } = useDepartmentTree();
  const createDept = useCreateDepartment();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DepartmentFormData>({
    resolver: zodResolver(departmentSchema),
    defaultValues: { department_type: 'DEPARTMENT', is_active: true, name_uz: '', name_en: '' },
  });

  const onSubmit = async (data: DepartmentFormData) => {
    const payload: CreateDepartmentData = {
      code: data.code,
      name: { ru: data.name_ru, uz: data.name_uz, en: data.name_en },
      department_type: data.department_type,
      is_active: data.is_active,
      parent: data.parent ?? null,
    };
    await createDept.mutateAsync(payload);
    setIsModalOpen(false);
    reset();
  };

  const totalCount = tree?.reduce((sum, d) => sum + countDepartments(d), 0) ?? 0;

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Подразделения"
        description="Организационная структура университета"
        actions={
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> Добавить
          </Button>
        }
      />

      <div className="grid grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-sm text-slate-500">Всего подразделений</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalCount}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-slate-500">Факультетов</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {tree?.filter((d) => d.department_type === 'FACULTY').length ?? 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-slate-500">Корневых узлов</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{tree?.length ?? 0}</p>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <h3 className="text-base font-semibold text-slate-900">Дерево подразделений</h3>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !tree || tree.length === 0 ? (
            <EmptyState
              icon={<Building2 className="h-12 w-12 text-slate-300" />}
              title="Нет подразделений"
              description="Создайте первое подразделение"
              action={<Button onClick={() => setIsModalOpen(true)}>Создать</Button>}
            />
          ) : (
            <div>
              {tree.map((dept) => (
                <DepartmentNode key={dept.id} dept={dept} level={0} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Modal
        open={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          reset();
        }}
        title="Новое подразделение"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Код *</label>
              <Input {...register('code')} placeholder="FAC-CS" className="mt-1" />
              {errors.code && <p className="text-xs text-red-500 mt-1">{errors.code.message}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Тип *</label>
              <select
                {...register('department_type')}
                className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              >
                {Object.entries(DEPT_TYPE_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Название (RU) *</label>
            <Input
              {...register('name_ru')}
              placeholder="Факультет компьютерных наук"
              className="mt-1"
            />
            {errors.name_ru && (
              <p className="text-xs text-red-500 mt-1">{errors.name_ru.message}</p>
            )}
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Название (UZ)</label>
            <Input
              {...register('name_uz')}
              placeholder="Kompyuter fanlari fakulteti"
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Название (EN)</label>
            <Input
              {...register('name_en')}
              placeholder="Faculty of Computer Science"
              className="mt-1"
            />
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" {...register('is_active')} id="is_active" className="rounded" />
            <label htmlFor="is_active" className="text-sm text-slate-700">
              Активно
            </label>
          </div>
          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={createDept.isPending} className="flex-1">
              {createDept.isPending ? 'Создание...' : 'Создать'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsModalOpen(false);
                reset();
              }}
            >
              Отмена
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
