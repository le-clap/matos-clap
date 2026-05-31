// components/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import type {AccessLevel} from "@/client";


interface ProtectedRouteProps {
  allowedRoles?: AccessLevel[];
}

export default function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Chargement de l'application...</div>;
  }

  // L'utilisateur n'est pas connecté
  if (!user) {
    return <Navigate to="/" replace />;
  }

  // Vérification des permissions si des rôles spécifiques sont requis
  if (allowedRoles && !allowedRoles.includes(user.access_level)) {
    return <Navigate to="/" replace />;
  }

  // L'utilisateur est autorisé, on affiche la page enfant
  return <Outlet />;
}
