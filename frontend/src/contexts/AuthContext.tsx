import {createContext, type ReactNode, useContext, useEffect, useState} from 'react';
import type {UserPublic} from '@/client';

interface AuthContextType {
  user: UserPublic | null;
  isLoading: boolean;
  login: () => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Vérifie si l'utilisateur a une session active au chargement
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch('/api/users/me');
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        }
      } catch (error) {
        console.error("Erreur de récupération de session:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  const login = () => {
    const devLoginEnabled = import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true';
    window.location.href = devLoginEnabled ? '/api/auth/dev-login' : '/api/auth/login';
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      setUser(null);
    } catch (error) {
      console.error("Erreur lors de la déconnexion", error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};
