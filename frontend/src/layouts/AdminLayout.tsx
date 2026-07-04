import {
  CalendarRange,
  ClipboardList,
  LayoutDashboard,
  Package,
  ScrollText,
  Users,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";
import { Logo } from "@/components/Logo";
import { UserMenu } from "@/components/UserMenu";
import type { AccessLevel } from "@/client";
import { cn } from "@/lib/utils";

interface NavItem {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  min?: AccessLevel;
  end?: boolean;
}

const nav: NavItem[] = [
  { to: "/admin", label: "Tableau de bord", icon: LayoutDashboard, end: true },
  { to: "/admin/requests", label: "Demandes", icon: ClipboardList },
  { to: "/admin/loans", label: "Prêts", icon: ScrollText },
  { to: "/admin/planning", label: "Planning", icon: CalendarRange },
  { to: "/admin/inventory", label: "Inventaire", icon: Package, min: "manager" },
  { to: "/admin/users", label: "Utilisateurs", icon: Users },
];

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  const { hasRole } = useAuth();
  return (
    <nav className="flex flex-col gap-1">
      {nav
        .filter((item) => !item.min || hasRole(item.min))
        .map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-danger-bg text-brand-200 shadow-[inset_2px_0_0_var(--color-primary)]"
                  : "text-content-muted hover:bg-surface-raised hover:text-content",
              )
            }
          >
            <item.icon className="size-[18px]" />
            {item.label}
          </NavLink>
        ))}
    </nav>
  );
}

export function AdminLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-border bg-surface lg:flex">
        <div className="flex h-16 items-center border-b border-border px-5">
          <Logo to="/admin" />
        </div>
        <div className="flex-1 overflow-y-auto p-3">
          <NavItems />
        </div>
        <div className="border-t border-border p-3 text-[11px] text-content-faint">
          Administration · Matos CLAP
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-ink-950/70 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="absolute inset-y-0 left-0 flex w-64 animate-fade-in flex-col border-r border-border bg-surface">
            <div className="flex h-16 items-center justify-between border-b border-border px-5">
              <Logo to="/admin" />
              <button onClick={() => setMobileOpen(false)} aria-label="Fermer">
                <X className="size-5 text-content-muted" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-3">
              <NavItems onNavigate={() => setMobileOpen(false)} />
            </div>
          </aside>
        </div>
      )}

      <div className="flex flex-1 flex-col lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-surface/80 px-4 backdrop-blur-xl sm:px-6">
          <button
            className="rounded-lg p-2 text-content-muted hover:bg-surface-raised lg:hidden"
            onClick={() => setMobileOpen(true)}
            aria-label="Menu"
          >
            <Menu className="size-5" />
          </button>
          <div className="ml-auto">
            <UserMenu context="admin" />
          </div>
        </header>
        <main className="flex-1 px-4 py-7 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
