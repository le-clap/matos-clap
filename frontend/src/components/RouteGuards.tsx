import { type ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import type { AccessLevel } from "@/client";
import { useAuth } from "@/auth/AuthContext";
import { PageSpinner } from "@/components/ui/Spinner";
import { Forbidden } from "@/pages/Forbidden";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <PageSpinner label="Chargement…" />;
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  return <>{children}</>;
}

export function RequireRole({
  min,
  children,
}: {
  min: AccessLevel;
  children: ReactNode;
}) {
  const { isLoading, hasRole } = useAuth();
  if (isLoading) return <PageSpinner label="Chargement…" />;
  if (!hasRole(min)) return <Forbidden />;
  return <>{children}</>;
}
