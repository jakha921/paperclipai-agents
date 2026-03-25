import { useEffect, useState, useCallback } from 'react';
import { cn } from '@/shared/lib/utils';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

type ToastVariant = 'success' | 'error' | 'warning' | 'info';

interface ToastData {
  id: string;
  message: string;
  variant: ToastVariant;
}

const variantConfig: Record<ToastVariant, { icon: typeof CheckCircle; style: string }> = {
  success: { icon: CheckCircle, style: 'bg-emerald-50 text-emerald-800 border-emerald-200' },
  error: { icon: AlertCircle, style: 'bg-red-50 text-red-800 border-red-200' },
  warning: { icon: AlertTriangle, style: 'bg-amber-50 text-amber-800 border-amber-200' },
  info: { icon: Info, style: 'bg-blue-50 text-blue-800 border-blue-200' },
};

let toastListeners: Array<(toast: ToastData) => void> = [];
let toastId = 0;

export function toast(message: string, variant: ToastVariant = 'info') {
  const data: ToastData = { id: String(++toastId), message, variant };
  for (const listener of toastListeners) {
    listener(data);
  }
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  const addToast = useCallback((data: ToastData) => {
    setToasts((prev) => [...prev, data]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== data.id));
    }, 5000);
  }, []);

  useEffect(() => {
    toastListeners.push(addToast);
    return () => {
      toastListeners = toastListeners.filter((l) => l !== addToast);
    };
  }, [addToast]);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => {
        const config = variantConfig[t.variant];
        const Icon = config.icon;
        return (
          <div
            key={t.id}
            className={cn(
              'flex items-center gap-3 rounded-lg border px-4 py-3 shadow-lg min-w-[300px]',
              config.style,
            )}
          >
            <Icon className="h-5 w-5 shrink-0" />
            <p className="text-sm flex-1">{t.message}</p>
            <button onClick={() => removeToast(t.id)} className="shrink-0 hover:opacity-70">
              <X className="h-4 w-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
