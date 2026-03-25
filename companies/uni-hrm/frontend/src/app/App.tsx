import { GoogleOAuthProvider } from '@react-oauth/google';
import { AppRouter } from './router';
import { ErrorBoundary } from './ErrorBoundary';

export function App() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ''}>
      <ErrorBoundary>
        <AppRouter />
      </ErrorBoundary>
    </GoogleOAuthProvider>
  );
}
