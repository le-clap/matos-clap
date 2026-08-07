import { ClipboardList, Package, ShoppingBag } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { Logo } from '@/components/Logo';
import { UserMenu } from '@/components/UserMenu';
import { useCart } from '@/features/cart/CartContext';
import { cn } from '@/lib/utils';

const links = [
  { to: '/catalog', label: 'Catalogue', icon: Package },
  { to: '/my/requests', label: 'Mes demandes', icon: ClipboardList },
  { to: '/my/loans', label: 'Mes prêts', icon: ShoppingBag },
];

export function AppLayout() {
  const { count } = useCart();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-border bg-surface/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 sm:px-6">
          <Logo />
          <nav className="hidden items-center gap-1 md:flex">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  cn(
                    'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-surface-raised text-content'
                      : 'text-content-muted hover:text-content',
                  )
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <NavLink
              to="/request"
              className={({ isActive }) =>
                cn(
                  'relative inline-flex h-10 items-center gap-2 rounded-lg border px-3.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-primary/40 bg-danger-bg text-brand-300'
                    : 'border-border text-content hover:bg-surface-raised',
                )
              }
            >
              <ShoppingBag className="size-4" />
              <span className="hidden sm:inline">Ma demande</span>
              {count > 0 && (
                <span className="flex min-w-5 items-center justify-center rounded-full bg-primary px-1.5 text-[11px] font-bold text-white tabular-nums">
                  {count}
                </span>
              )}
            </NavLink>
            <UserMenu context="app" />
          </div>
        </div>

        {/* Mobile nav */}
        <nav className="flex items-center gap-1 overflow-x-auto border-t border-border px-3 py-1.5 md:hidden">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  'inline-flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-1.5 text-[13px] font-medium transition-colors',
                  isActive ? 'bg-surface-raised text-content' : 'text-content-muted',
                )
              }
            >
              <link.icon className="size-4" />
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-7 sm:px-6">
        <Outlet />
      </main>

      <footer className="border-t border-border py-6 text-center text-xs text-content-faint">
        Matos CLAP · Centrale Lille Audiovisuel Production
      </footer>
    </div>
  );
}
