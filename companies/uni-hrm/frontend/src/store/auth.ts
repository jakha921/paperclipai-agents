import { create } from 'zustand';
import { apiClient } from '@/shared/lib/api-client';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  avatar: string | null;
  language: string;
  roles: string[];
  permissions: string[];
}

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  password: string;
  password_confirm: string;
}

interface AuthTokens {
  access: string;
  refresh: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginData) => Promise<void>;
  loginWithGoogle: (credential: string) => Promise<void>;
  devLogin: (role: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
  setUser: (user: User | null) => void;
  hasPermission: (codename: string) => boolean;
  hasRole: (roleCode: string) => boolean;
}

export type { User, LoginData, RegisterData };

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  login: async (data: LoginData) => {
    const response = await apiClient.post<AuthTokens>('/auth/login/', data);
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    set({ isAuthenticated: true });
    await get().fetchMe();
  },

  loginWithGoogle: async (credential: string) => {
    const response = await apiClient.post<AuthTokens & { user: User }>('/auth/google/', {
      credential,
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    set({ user: response.data.user, isAuthenticated: true });
  },

  devLogin: async (role: string) => {
    const response = await apiClient.post<AuthTokens & { user: User }>('/auth/dev-token/', {
      role,
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    set({ user: response.data.user, isAuthenticated: true });
  },

  register: async (data: RegisterData) => {
    const response = await apiClient.post<AuthTokens>('/auth/register/', data);
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    set({ isAuthenticated: true });
    await get().fetchMe();
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  fetchMe: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get<User>('/auth/me/');
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  hasPermission: (codename: string) => {
    const { user } = get();
    return user?.permissions?.includes(codename) ?? false;
  },

  hasRole: (roleCode: string) => {
    const { user } = get();
    return user?.roles?.includes(roleCode) ?? false;
  },
}));
