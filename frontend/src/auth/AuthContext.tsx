import { useQuery } from '@tanstack/react-query';
import { createContext, type ReactNode, useContext } from 'react';
import { type AccessLevel, type UserPublic, UsersService } from '@/client';
import { ApiError, unwrap } from '@/lib/api';
import { hasRole as hasRoleFn } from '@/lib/roles';

interface AuthContextValue {
  user: UserPublic | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  hasRole: (min: AccessLevel) => boolean;
  login: () => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const devLoginEnabled = import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true';

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      try {
        return await unwrap(UsersService.usersGetMe());
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null;
        throw err;
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const login = () => {
    window.location.href = devLoginEnabled ? '/api/auth/dev-login' : '/api/auth/login';
  };

  const logout = async () => {
    let logoutUrl: string | null = null;
    try {
      const res = await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
      if (res.ok) logoutUrl = (await res.json()).logout_url;
    } finally {
      window.location.href = logoutUrl ?? '/login';
    }
  };

  const value: AuthContextValue = {
    user: user ?? null,
    isLoading,
    isAuthenticated: !!user,
    hasRole: (min) => hasRoleFn(user?.access_level, min),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
