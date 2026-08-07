import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';

export function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <p className="text-7xl font-black tracking-tighter text-primary">404</p>
      <h1 className="mt-2 text-xl font-bold">Page introuvable</h1>
      <p className="mt-2 max-w-sm text-sm text-content-muted">
        La page que vous cherchez n'existe pas ou a été déplacée.
      </p>
      <Button asChild className="mt-6">
        <Link to="/">Retour à l'accueil</Link>
      </Button>
    </div>
  );
}
