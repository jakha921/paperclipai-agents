import { Link } from 'react-router-dom';
import { Button, EmptyState } from '@/shared/ui';
import { FileQuestion } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <EmptyState
        icon={<FileQuestion className="h-16 w-16" />}
        title="404 — Страница не найдена"
        description="Запрошенная страница не существует или была перемещена."
        action={
          <Link to="/dashboard">
            <Button>На главную</Button>
          </Link>
        }
      />
    </div>
  );
}
