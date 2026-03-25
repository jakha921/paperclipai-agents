import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { Button, Input, Select, Tabs, Card, CardContent, PageHeader, Avatar, toast } from '@/shared/ui';
import { useAuthStore } from '@/store/auth';
import { useUpdateProfile, useChangePassword } from '@/features/auth/api';
import { isAxiosError } from 'axios';

interface ProfileFormData {
  first_name: string;
  last_name: string;
  phone: string;
  language: string;
}

interface PasswordFormData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export function ProfilePage() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const fetchMe = useAuthStore((s) => s.fetchMe);
  const [activeTab, setActiveTab] = useState('info');

  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();

  const profileForm = useForm<ProfileFormData>({
    defaultValues: {
      first_name: user?.first_name ?? '',
      last_name: user?.last_name ?? '',
      phone: user?.phone ?? '',
      language: user?.language ?? 'ru',
    },
  });

  const passwordForm = useForm<PasswordFormData>();

  const onProfileSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfile.mutateAsync(data);
      await fetchMe();
      toast(t('profile.updateSuccess'), 'success');
    } catch {
      toast(t('profile.updateError'), 'error');
    }
  };

  const onPasswordSubmit = async (data: PasswordFormData) => {
    if (data.new_password !== data.confirm_password) {
      toast(t('auth.passwordMismatch'), 'error');
      return;
    }
    try {
      await changePassword.mutateAsync({
        old_password: data.old_password,
        new_password: data.new_password,
      });
      passwordForm.reset();
      toast(t('profile.passwordChanged'), 'success');
    } catch (error: unknown) {
      if (isAxiosError(error) && error.response?.data) {
        const errData = error.response.data as Record<string, string[]>;
        const message = errData.old_password?.[0] ?? t('profile.passwordError');
        toast(message, 'error');
      } else {
        toast(t('profile.passwordError'), 'error');
      }
    }
  };

  const tabs = [
    { value: 'info', label: t('profile.info') },
    { value: 'security', label: t('profile.security') },
  ];

  const languageOptions = [
    { value: 'ru', label: 'Русский' },
    { value: 'uz', label: "O'zbek" },
    { value: 'en', label: 'English' },
  ];

  return (
    <div className="p-6">
      <PageHeader title={t('profile.title')} />

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} className="mb-6" />

      {activeTab === 'info' && (
        <Card>
          <CardContent>
            <div className="mb-6 flex items-center gap-4">
              <Avatar
                name={`${user?.first_name ?? ''} ${user?.last_name ?? ''}`}
                size="lg"
                src={user?.avatar}
              />
              <div>
                <p className="text-base font-semibold text-slate-900">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-sm text-slate-500">{user?.email}</p>
              </div>
            </div>
            <form
              onSubmit={profileForm.handleSubmit(onProfileSubmit)}
              className="max-w-md space-y-4"
            >
              <Input
                id="first_name"
                label={t('auth.firstName')}
                {...profileForm.register('first_name')}
              />
              <Input
                id="last_name"
                label={t('auth.lastName')}
                {...profileForm.register('last_name')}
              />
              <Input id="email" label={t('auth.email')} value={user?.email ?? ''} disabled />
              <Input
                id="phone"
                label={t('auth.phone')}
                {...profileForm.register('phone')}
              />
              <Select
                id="language"
                label={t('profile.language')}
                options={languageOptions}
                {...profileForm.register('language')}
              />
              <Button type="submit" loading={updateProfile.isPending}>
                {t('actions.save')}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {activeTab === 'security' && (
        <Card>
          <CardContent>
            <h3 className="mb-4 text-base font-semibold text-slate-900">
              {t('profile.changePassword')}
            </h3>
            <form
              onSubmit={passwordForm.handleSubmit(onPasswordSubmit)}
              className="max-w-md space-y-4"
            >
              <Input
                id="old_password"
                label={t('profile.oldPassword')}
                type="password"
                {...passwordForm.register('old_password')}
              />
              <Input
                id="new_password"
                label={t('profile.newPassword')}
                type="password"
                {...passwordForm.register('new_password')}
              />
              <Input
                id="confirm_password"
                label={t('profile.confirmPassword')}
                type="password"
                {...passwordForm.register('confirm_password')}
              />
              <Button type="submit" loading={changePassword.isPending}>
                {t('profile.changePassword')}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
