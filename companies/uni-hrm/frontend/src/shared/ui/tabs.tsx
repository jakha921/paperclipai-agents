import { cn } from '@/shared/lib/utils';

interface Tab {
  value: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (value: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onTabChange, className }: TabsProps) {
  return (
    <div className={cn('border-b border-slate-200', className)}>
      <nav className="flex gap-6" aria-label="Tabs">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => onTabChange(tab.value)}
            className={cn(
              'py-3 text-sm font-medium border-b-2 transition-colors -mb-px',
              activeTab === tab.value
                ? 'text-primary-600 border-primary-600'
                : 'text-slate-500 border-transparent hover:text-slate-700 hover:border-slate-300',
            )}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}
