import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { apiClient } from '@/shared/lib/api-client';
import {
  PageHeader,
  Button,
  Card,
  Modal,
  Input,
  Select,
  Badge,
  toast,
  EmptyState,
  Skeleton,
} from '@/shared/ui';

interface Permission {
  id: string;
  codename: string;
  name: string;
  module: string;
}

interface Role {
  id: string;
  name: string;
  code: string;
  description: string;
  level: string;
  permissions: Permission[];
}

interface RoleFormData {
  name: string;
  code: string;
  description: string;
  level: string;
  permission_ids: string[];
}

interface PaginatedResponse<T> {
  results: T[];
  count: number;
}

function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<Role>>('/auth/roles/');
      return response.data.results;
    },
  });
}

export function RolesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { data: roles, isLoading } = useRoles();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState<RoleFormData>({
    name: '',
    code: '',
    description: '',
    level: 'global',
    permission_ids: [],
  });

  const saveMutation = useMutation({
    mutationFn: async (data: RoleFormData) => {
      if (editingRole) {
        return apiClient.put(`/auth/roles/${editingRole.id}/`, data);
      }
      return apiClient.post('/auth/roles/', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setModalOpen(false);
      toast(t('roles.saved'), 'success');
    },
    onError: () => {
      toast(t('roles.saveError'), 'error');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => apiClient.delete(`/auth/roles/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      toast(t('roles.deleted'), 'success');
    },
  });

  // Collect all unique permissions from roles
  const allPermissions = roles
    ? Array.from(
        new Map(
          roles.flatMap((r) => r.permissions).map((p) => [p.id, p]),
        ).values(),
      )
    : [];

  const groupedPermissions = allPermissions.reduce<Record<string, Permission[]>>(
    (acc, perm) => {
      const group = acc[perm.module] ?? [];
      group.push(perm);
      acc[perm.module] = group;
      return acc;
    },
    {},
  );

  const openCreate = () => {
    setEditingRole(null);
    setFormData({ name: '', code: '', description: '', level: 'global', permission_ids: [] });
    setModalOpen(true);
  };

  const openEdit = (role: Role) => {
    setEditingRole(role);
    setFormData({
      name: role.name,
      code: role.code,
      description: role.description,
      level: role.level,
      permission_ids: role.permissions.map((p) => p.id),
    });
    setModalOpen(true);
  };

  const togglePermission = (permId: string) => {
    setFormData((prev) => ({
      ...prev,
      permission_ids: prev.permission_ids.includes(permId)
        ? prev.permission_ids.filter((id) => id !== permId)
        : [...prev.permission_ids, permId],
    }));
  };

  const levelOptions = [
    { value: 'global', label: t('roles.global') },
    { value: 'department', label: t('roles.department') },
    { value: 'personal', label: t('roles.personal') },
  ];

  const levelVariants: Record<string, 'default' | 'success' | 'warning'> = {
    global: 'success',
    department: 'warning',
    personal: 'default',
  };

  return (
    <div className="p-6">
      <PageHeader
        title={t('roles.title')}
        description={t('roles.description')}
        actions={
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" />
            {t('roles.add')}
          </Button>
        }
      />

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      ) : !roles?.length ? (
        <EmptyState title={t('roles.empty')} description={t('roles.emptyDescription')} />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 text-left">
                  <th className="px-6 py-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                    {t('roles.name')}
                  </th>
                  <th className="px-6 py-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                    {t('roles.code')}
                  </th>
                  <th className="px-6 py-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                    {t('roles.level')}
                  </th>
                  <th className="px-6 py-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                    {t('roles.permissions')}
                  </th>
                  <th className="px-6 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {roles.map((role) => (
                  <tr key={role.id} className="transition-colors hover:bg-slate-50">
                    <td className="px-6 py-4 text-sm font-medium text-slate-900">{role.name}</td>
                    <td className="px-6 py-4 text-sm text-slate-500">{role.code}</td>
                    <td className="px-6 py-4">
                      <Badge variant={levelVariants[role.level] ?? 'default'}>{role.level}</Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-500">{role.permissions.length}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openEdit(role)}
                          className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-primary-600"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => deleteMutation.mutate(role.id)}
                          className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-red-600"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingRole ? t('roles.edit') : t('roles.create')}
        size="lg"
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            saveMutation.mutate(formData);
          }}
          className="space-y-4"
        >
          <Input
            id="role-name"
            label={t('roles.name')}
            value={formData.name}
            onChange={(e) => setFormData((f) => ({ ...f, name: e.target.value }))}
          />
          <Input
            id="role-code"
            label={t('roles.code')}
            value={formData.code}
            onChange={(e) => setFormData((f) => ({ ...f, code: e.target.value }))}
            disabled={!!editingRole}
          />
          <Input
            id="role-description"
            label={t('roles.descriptionField')}
            value={formData.description}
            onChange={(e) => setFormData((f) => ({ ...f, description: e.target.value }))}
          />
          <Select
            id="role-level"
            label={t('roles.level')}
            options={levelOptions}
            value={formData.level}
            onChange={(e) => setFormData((f) => ({ ...f, level: e.target.value }))}
          />

          {Object.keys(groupedPermissions).length > 0 && (
            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">{t('roles.permissions')}</p>
              <div className="max-h-60 overflow-y-auto rounded-lg border border-slate-200 p-4 space-y-4">
                {Object.entries(groupedPermissions).map(([module, perms]) => (
                  <div key={module}>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      {module}
                    </p>
                    <div className="flex flex-wrap gap-3">
                      {perms.map((perm) => (
                        <label
                          key={perm.id}
                          className="flex cursor-pointer items-center gap-1.5 text-sm text-slate-700"
                        >
                          <input
                            type="checkbox"
                            checked={formData.permission_ids.includes(perm.id)}
                            onChange={() => togglePermission(perm.id)}
                            className="rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                          />
                          {perm.codename.split('.')[1]}
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>
              {t('actions.cancel')}
            </Button>
            <Button type="submit" loading={saveMutation.isPending}>
              {t('actions.save')}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
