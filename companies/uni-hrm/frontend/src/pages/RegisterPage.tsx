import { useTranslation } from 'react-i18next';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { isAxiosError } from 'axios';
import { Button, Input, toast } from '@/shared/ui';
import { useRegister } from '@/features/auth';

function createRegisterSchema(t: (key: string) => string) {
  return z
    .object({
      first_name: z.string().min(1, t('validation.required')),
      last_name: z.string().min(1, t('validation.required')),
      email: z.string().email(t('validation.email')),
      phone: z
        .string()
        .min(1, t('validation.required'))
        .regex(/^\+998\d{9}$/, t('validation.phone')),
      password: z.string().min(8, t('validation.password_min')),
      password_confirm: z.string().min(1, t('validation.required')),
    })
    .refine((data) => data.password === data.password_confirm, {
      message: t('validation.password_match'),
      path: ['password_confirm'],
    });
}

type RegisterFormData = z.infer<ReturnType<typeof createRegisterSchema>>;

export function RegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const registerMutation = useRegister();

  const schema = createRegisterSchema(t);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: RegisterFormData) => {
    registerMutation.mutate(data, {
      onSuccess: () => {
        navigate('/dashboard', { replace: true });
      },
      onError: (error) => {
        if (isAxiosError(error)) {
          const message =
            (error.response?.data as Record<string, string>)?.detail ?? t('auth.register_error');
          toast(message, 'error');
        } else {
          toast(t('auth.register_error'), 'error');
        }
      },
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          id="first_name"
          label={t('auth.first_name')}
          error={errors.first_name?.message}
          {...register('first_name')}
        />
        <Input
          id="last_name"
          label={t('auth.last_name')}
          error={errors.last_name?.message}
          {...register('last_name')}
        />
      </div>
      <Input
        id="email"
        label={t('auth.email')}
        type="email"
        placeholder="user@example.com"
        error={errors.email?.message}
        {...register('email')}
      />
      <Input
        id="phone"
        label={t('auth.phone')}
        type="tel"
        placeholder="+998901234567"
        error={errors.phone?.message}
        {...register('phone')}
      />
      <Input
        id="password"
        label={t('auth.password')}
        type="password"
        placeholder="********"
        error={errors.password?.message}
        {...register('password')}
      />
      <Input
        id="password_confirm"
        label={t('auth.password_confirm')}
        type="password"
        placeholder="********"
        error={errors.password_confirm?.message}
        {...register('password_confirm')}
      />
      <Button type="submit" className="w-full" loading={registerMutation.isPending}>
        {t('auth.register')}
      </Button>

      <p className="text-center text-sm text-slate-500">
        {t('auth.has_account')}{' '}
        <Link to="/login" className="font-medium text-primary-600 hover:text-primary-700">
          {t('auth.login')}
        </Link>
      </p>
    </form>
  );
}
