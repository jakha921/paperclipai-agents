import type { ReactNode } from 'react';

interface AppShellProps {
  sidebar: ReactNode;
  children: ReactNode;
}

export function AppShell({ sidebar, children }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      {sidebar}
      <main className="flex-1 overflow-y-auto bg-background p-6">{children}</main>
    </div>
  );
}
