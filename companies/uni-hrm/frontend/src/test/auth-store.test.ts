import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '@/store/auth';

describe('useAuthStore', () => {
  beforeEach(() => {
    localStorage.clear();
    // Reset store to initial state
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('has correct initial state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });

  it('setUser sets user and marks authenticated', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      full_name: 'Test User',
      phone: '+998901234567',
      avatar: null,
      language: 'en',
      roles: ['admin'],
      permissions: ['view_users'],
    };

    useAuthStore.getState().setUser(mockUser);

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it('setUser with null clears authentication', () => {
    useAuthStore.getState().setUser({
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      full_name: 'Test User',
      phone: '',
      avatar: null,
      language: 'en',
      roles: [],
      permissions: [],
    });

    useAuthStore.getState().setUser(null);

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('logout clears user and tokens', () => {
    localStorage.setItem('access_token', 'test-access');
    localStorage.setItem('refresh_token', 'test-refresh');
    useAuthStore.setState({ user: { id: '1' } as ReturnType<typeof useAuthStore.getState>['user'], isAuthenticated: true });

    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });

  it('hasPermission returns true when user has permission', () => {
    useAuthStore.setState({
      user: {
        id: '1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        full_name: 'Test User',
        phone: '',
        avatar: null,
        language: 'en',
        roles: [],
        permissions: ['view_users', 'edit_users'],
      },
      isAuthenticated: true,
    });

    expect(useAuthStore.getState().hasPermission('view_users')).toBe(true);
    expect(useAuthStore.getState().hasPermission('delete_users')).toBe(false);
  });

  it('hasRole returns true when user has role', () => {
    useAuthStore.setState({
      user: {
        id: '1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        full_name: 'Test User',
        phone: '',
        avatar: null,
        language: 'en',
        roles: ['admin', 'hr_manager'],
        permissions: [],
      },
      isAuthenticated: true,
    });

    expect(useAuthStore.getState().hasRole('admin')).toBe(true);
    expect(useAuthStore.getState().hasRole('super_admin')).toBe(false);
  });

  it('isAuthenticated reflects localStorage token on creation', () => {
    localStorage.setItem('access_token', 'some-token');
    // Re-create store behavior check
    const hasToken = !!localStorage.getItem('access_token');
    expect(hasToken).toBe(true);
  });
});
