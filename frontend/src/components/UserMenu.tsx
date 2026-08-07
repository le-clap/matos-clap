import { ChevronDown, LayoutDashboard, LogOut, Store } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/auth/AuthContext';
import { Avatar } from '@/components/ui/Avatar';
import { DropdownMenu } from '@/components/ui/DropdownMenu';
import { ROLE_LABELS } from '@/lib/roles';

export function UserMenu({ context = 'app' }: { context?: 'app' | 'admin' }) {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  if (!user) return null;

  const items: Parameters<typeof DropdownMenu>[0]['items'] = [];
  if (hasRole('clap')) {
    items.push(
      context === 'app'
        ? {
            label: 'Backoffice',
            icon: LayoutDashboard,
            onClick: () => navigate('/admin'),
          }
        : {
            label: 'Retour au site',
            icon: Store,
            onClick: () => navigate('/catalog'),
          },
      'separator',
    );
  }
  items.push({
    label: 'Se déconnecter',
    icon: LogOut,
    tone: 'danger',
    onClick: () => void logout(),
  });

  return (
    <DropdownMenu
      align="end"
      trigger={
        <button className="flex items-center gap-2.5 rounded-xl border border-transparent py-1 pl-1 pr-2.5 transition-colors hover:border-border hover:bg-surface-raised">
          <Avatar name={user.name} size="sm" />
          <div className="hidden text-left leading-tight sm:block">
            <div className="max-w-[140px] truncate text-[13px] font-medium text-content">
              {user.name}
            </div>
            <div className="text-[11px] text-content-faint">{ROLE_LABELS[user.access_level]}</div>
          </div>
          <ChevronDown className="size-4 text-content-faint" />
        </button>
      }
      items={items}
    />
  );
}
