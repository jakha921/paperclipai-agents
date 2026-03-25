import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { Building2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from '@/shared/ui';
import { useLoginWithGoogle, useDevLogin } from '@/features/auth';

const DEMO_ROLES = [
  {
    code: 'super_admin',
    label: 'Суперадмин',
    emoji: '\u{1F527}',
    bg: 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100',
  },
  {
    code: 'admin',
    label: 'Администратор',
    emoji: '\u{1F451}',
    bg: 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100',
  },
  {
    code: 'hr_manager',
    label: 'HR Менеджер',
    emoji: '\u{1F465}',
    bg: 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100',
  },
  {
    code: 'dean',
    label: 'Декан',
    emoji: '\u{1F3DB}',
    bg: 'bg-teal-50 border-teal-200 text-teal-700 hover:bg-teal-100',
  },
  {
    code: 'head_of_department',
    label: 'Зав. кафедрой',
    emoji: '\u{1F4CB}',
    bg: 'bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100',
  },
  {
    code: 'accountant',
    label: 'Бухгалтер',
    emoji: '\u{1F4B0}',
    bg: 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100',
  },
  {
    code: 'employee',
    label: 'Сотрудник',
    emoji: '\u{1F464}',
    bg: 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100',
  },
];

export function LoginPage() {
  const navigate = useNavigate();
  const loginWithGoogle = useLoginWithGoogle();
  const devLogin = useDevLogin();

  const handleGoogle = (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) return;
    loginWithGoogle.mutate(credentialResponse.credential, {
      onSuccess: () => navigate('/dashboard', { replace: true }),
      onError: () => toast('Google login failed', 'error'),
    });
  };

  const handleDevLogin = (role: string) => {
    devLogin.mutate(role, {
      onSuccess: () => navigate('/dashboard', { replace: true }),
      onError: () => toast('Dev login failed', 'error'),
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 font-heading">Uni-HRM</h1>
              <p className="text-xs text-slate-500">Система управления персоналом</p>
            </div>
          </div>

          {/* Google Login */}
          <div className="space-y-4">
            <p className="text-sm font-medium text-slate-700">Войти через</p>
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogle}
                onError={() => toast('Google login failed', 'error')}
                useOneTap={false}
                text="signin_with"
                shape="rectangular"
                theme="outline"
                size="large"
                width="320"
              />
            </div>
          </div>

          {/* Dev quick login */}
          {import.meta.env.DEV && (
            <div className="mt-8 pt-6 border-t border-slate-100">
              <p className="text-xs font-medium text-slate-400 mb-3 uppercase tracking-wide">
                Dev — быстрый вход
              </p>
              <div className="grid grid-cols-2 gap-2">
                {DEMO_ROLES.map((role) => (
                  <button
                    key={role.code}
                    onClick={() => handleDevLogin(role.code)}
                    disabled={devLogin.isPending}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-colors ${role.bg}`}
                  >
                    <span>{role.emoji}</span>
                    {role.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
