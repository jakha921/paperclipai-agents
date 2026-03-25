import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginPage } from '@/pages/LoginPage';

// Mock @react-oauth/google
vi.mock('@react-oauth/google', () => ({
  GoogleLogin: (props: Record<string, unknown>) => (
    <button data-testid="google-login" onClick={() => (props.onSuccess as (r: { credential: string }) => void)({ credential: 'test' })}>
      Google Login
    </button>
  ),
  GoogleOAuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock the auth feature API
vi.mock('@/features/auth', () => ({
  useLoginWithGoogle: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useDevLogin: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

// Mock toast
vi.mock('@/shared/ui', async (importOriginal) => {
  const actual = await importOriginal<Record<string, unknown>>();
  return {
    ...actual,
    toast: vi.fn(),
  };
});

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without errors', () => {
    const { container } = renderWithProviders(<LoginPage />);
    expect(container).toBeTruthy();
  });

  it('displays the Uni-HRM heading', () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByText('Uni-HRM')).toBeInTheDocument();
  });

  it('renders Google Login button', () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByTestId('google-login')).toBeInTheDocument();
  });
});
