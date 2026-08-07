import { ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';

export function Forbidden() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-danger-bg text-brand-400">
        <ShieldAlert className="size-7" />
      </div>
      <h1 className="mt-5 text-xl font-bold">Accès refusé</h1>
      <p className="mt-2 max-w-sm text-sm text-content-muted">
        Vous n'avez pas les permissions nécessaires pour accéder à cette page.
      </p>
      <Button asChild variant="secondary" className="mt-6">
        <Link to="/catalog">Retour au catalogue</Link>
      </Button>
    </div>
  );
}
