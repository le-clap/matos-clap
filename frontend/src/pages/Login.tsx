import { ArrowRight, LogIn } from 'lucide-react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/auth/AuthContext';
import { Button } from '@/components/ui/Button';
import { PageSpinner } from '@/components/ui/Spinner';

export function LoginPage() {
  const { isAuthenticated, isLoading, login } = useAuth();

  if (isLoading) return <PageSpinner />;
  if (isAuthenticated) return <Navigate to="/" replace />;

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-bg px-4">
      <div className="bg-grid pointer-events-none absolute inset-0 opacity-60" />
      <div
        className="pointer-events-none absolute -top-40 left-1/2 size-[640px] -translate-x-1/2 rounded-full opacity-25 blur-[120px]"
        style={{
          background: 'radial-gradient(circle, var(--color-brand-600), transparent 65%)',
        }}
      />

      <div className="relative w-full max-w-md animate-fade-in">
        <div className="rounded-2xl border border-border-strong bg-surface/80 p-8 shadow-pop backdrop-blur-xl">
          <div className="flex flex-col items-center text-center">
            <img src="/logo-clap.png" alt="CLAP" className="size-16 rounded-2xl object-contain" />
            <h1 className="mt-5 text-2xl font-bold tracking-tight">
              Matos<span className="text-primary"> CLAP</span>
            </h1>
            <p className="mt-2 text-sm text-content-muted">
              Plateforme de prêt de matériel audiovisuel de Centrale Lille Audiovisuel Production.
            </p>
          </div>

          <Button size="lg" className="mt-8 w-full" onClick={login}>
            <LogIn className="size-4" />
            Se connecter avec CLA
            <ArrowRight className="size-4" />
          </Button>

          <p className="mt-4 text-center text-xs text-content-faint">
            Authentification via Centrale Lille Associations
          </p>
        </div>
      </div>
    </div>
  );
}
