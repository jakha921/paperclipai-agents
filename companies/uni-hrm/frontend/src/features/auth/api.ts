import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import { useAuthStore, type User, type LoginData, type RegisterData } from '@/store/auth';

interface ChangePasswordData {
  old_password: string;
  new_password: string;
}

interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  phone?: string;
  language?: string;
}

interface VerifyOTPData {
  code: string;
}

export function useLogin() {
  const login = useAuthStore((s) => s.login);

  return useMutation({
    mutationFn: (data: LoginData) => login(data),
  });
}

export function useLoginWithGoogle() {
  const loginWithGoogle = useAuthStore((s) => s.loginWithGoogle);

  return useMutation({
    mutationFn: (credential: string) => loginWithGoogle(credential),
  });
}

export function useDevLogin() {
  const devLogin = useAuthStore((s) => s.devLogin);

  return useMutation({
    mutationFn: (role: string) => devLogin(role),
  });
}

export function useRegister() {
  const register = useAuthStore((s) => s.register);

  return useMutation({
    mutationFn: (data: RegisterData) => register(data),
  });
}

export function useMe() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const response = await apiClient.get<User>('/auth/me/');
      return response.data;
    },
    enabled: isAuthenticated,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: async (data: UpdateProfileData) => {
      const response = await apiClient.patch<User>('/auth/me/', data);
      return response.data;
    },
    onSuccess: (user) => {
      setUser(user);
      queryClient.setQueryData(['auth', 'me'], user);
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: async (data: ChangePasswordData) => {
      const response = await apiClient.post<{ detail: string }>('/auth/change-password/', data);
      return response.data;
    },
  });
}

export function useVerifyOTP() {
  return useMutation({
    mutationFn: async (data: VerifyOTPData) => {
      const response = await apiClient.post<{ detail: string }>('/auth/verify-otp/', data);
      return response.data;
    },
  });
}
