# Uni-HRM Design System — AI Instructions

> Adapted from SaaS Design System. Indigo palette, Plus Jakarta Sans + Red Hat Display, dark sidebar.

---

## 1. Design Philosophy

### DO
- Clean, corporate SaaS aesthetic — think Linear, Notion, Vercel Dashboard
- Indigo accent color (`#4F46E5` / `indigo-600`)
- White backgrounds with subtle gray borders (`border-gray-200`)
- Card-based layouts with `rounded-xl border shadow-sm`
- Generous whitespace — `p-6`, `gap-6`, `space-y-6`
- Consistent 4px spacing scale (Tailwind default)
- Subtle hover/focus transitions (`transition-colors duration-150`)
- Plus Jakarta Sans for body, Red Hat Display for headings

### DO NOT
- No glassmorphism, no backdrop-blur, no gradients on backgrounds
- No dark mode unless explicitly requested
- No rounded-full on cards or containers (use `rounded-xl` max)
- No shadows larger than `shadow-md`
- No colored backgrounds on page-level containers (white or `slate-50` only)
- No decorative illustrations or hero sections
- No animated loaders on every action — use skeleton screens
- No custom scrollbars
- No `!important` overrides in Tailwind

---

## 2. Design Tokens

### Colors

```ts
// tailwind.config.ts — extend colors
const colors = {
  // Primary — Indigo
  primary: {
    50:  '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',
    600: '#4F46E5', // ← main accent
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
    950: '#1E1B4B',
  },
  // Sidebar
  sidebar: '#1E1B4B', // indigo-950

  // Semantic
  success: '#10B981', // emerald-500
  warning: '#F59E0B', // amber-500
  error:   '#EF4444', // red-500
  info:    '#3B82F6', // blue-500

  // Neutrals
  background: '#F8FAFC', // slate-50
  surface:    '#FFFFFF',
  border:     '#E2E8F0', // slate-200
  'text-primary':   '#0F172A', // slate-900
  'text-secondary': '#64748B', // slate-500
};
```

### Typography

```css
/* index.css */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Red+Hat+Display:wght@600;700&display=swap');
@import 'tailwindcss';

:root {
  --font-sans: 'Plus Jakarta Sans', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-heading: 'Red Hat Display', ui-sans-serif, system-ui, -apple-system, sans-serif;
}

body {
  @apply font-sans text-slate-900 bg-slate-50 antialiased;
}

h1, h2, h3, h4 {
  font-family: var(--font-heading);
}
```

| Element       | Class                                        |
|---------------|----------------------------------------------|
| Page title    | `text-2xl font-bold font-heading text-slate-900` |
| Section title | `text-lg font-semibold font-heading text-slate-900` |
| Card title    | `text-base font-semibold text-slate-900`     |
| Body text     | `text-sm text-slate-600`                     |
| Caption       | `text-xs text-slate-500`                     |
| Label         | `text-sm font-medium text-slate-700`         |
| Link          | `text-sm font-medium text-primary-600 hover:text-primary-700` |

### Spacing

| Token   | Value | Use case                  |
|---------|-------|---------------------------|
| `gap-1` | 4px   | Icon + text               |
| `gap-2` | 8px   | Inline elements           |
| `gap-3` | 12px  | Form fields               |
| `gap-4` | 16px  | Card internal padding     |
| `gap-6` | 24px  | Section spacing           |
| `gap-8` | 32px  | Page sections             |

### Shadows

| Token       | Use case              |
|-------------|-----------------------|
| `shadow-sm` | Cards, dropdowns      |
| `shadow-md` | Modals, popovers      |
| (none)      | Everything else       |

### Border Radius

| Token         | Use case                    |
|---------------|-----------------------------|
| `rounded-sm`  | Badges (4px)                |
| `rounded-md`  | Buttons, inputs (6px)       |
| `rounded-lg`  | Cards, dropdowns (8px)      |
| `rounded-xl`  | Modals, toasts (12px)       |
| `rounded-full`| Avatars, tags only          |

---

## 3. Sidebar — Dark Theme

The sidebar uses dark indigo background (`#1E1B4B` / `indigo-950`) with white text.

```tsx
import { cn } from '@/shared/lib/utils';
import type { ReactNode } from 'react';

interface NavItem {
  id: string;
  label: string;
  icon: ReactNode;
  href: string;
  badge?: number;
}

interface SidebarProps {
  logo: ReactNode;
  items: NavItem[];
  activeId: string;
  footer?: ReactNode;
}

export function Sidebar({ logo, items, activeId, footer }: SidebarProps) {
  return (
    <div className="flex h-full flex-col bg-[#1E1B4B] text-white">
      {/* Logo */}
      <div className="flex h-14 items-center px-4 border-b border-indigo-800/50">
        {logo}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {items.map((item) => (
          <a
            key={item.id}
            href={item.href}
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              activeId === item.id
                ? 'bg-indigo-600 text-white'
                : 'text-indigo-200 hover:bg-indigo-800/50 hover:text-white',
            )}
          >
            <span className="h-5 w-5 flex-shrink-0">{item.icon}</span>
            {item.label}
            {item.badge !== undefined && item.badge > 0 && (
              <span className="ml-auto rounded-full bg-indigo-500/30 text-indigo-100 px-2 py-0.5 text-xs font-medium">
                {item.badge}
              </span>
            )}
          </a>
        ))}
      </nav>

      {/* Footer */}
      {footer && (
        <div className="border-t border-indigo-800/50 p-4">
          {footer}
        </div>
      )}
    </div>
  );
}
```

## 4. App Shell

```tsx
import type { ReactNode } from 'react';

interface AppShellProps {
  sidebar: ReactNode;
  children: ReactNode;
}

export function AppShell({ sidebar, children }: AppShellProps) {
  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar — dark */}
      <aside className="hidden lg:flex lg:w-64 lg:flex-col">
        {sidebar}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
```

## 5. Component Patterns

All components use indigo-600 as primary. See original SaaS Design System for full component code (Button, Card, Badge, Input, Select, Textarea, Avatar, Modal, EmptyState, Skeleton, Dropdown, Tabs, Toast, PageHeader, PageContent, StatCard, DataTable).

Key adaptations from original:
- Replace all `primary-600` references → `indigo-600` (or use `primary-600` with indigo in tailwind config)
- Replace `gray-*` → `slate-*` where appropriate
- Replace `bg-primary-50` → `bg-indigo-50` for backgrounds
- Replace `text-primary-700` → `text-indigo-700` for text
- Font: `font-sans` = Plus Jakarta Sans, `font-heading` = Red Hat Display
