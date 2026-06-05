import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
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
    // Redirige vers la route backend qui gère le SSO/CLA
    window.location.href = '/api/auth/dev/login'; // TODO : Remplacer par auth/login quand le endpoint authentification/matos-clap existera chez CLA
  };

  const logout = async () => {
    try {
      // Appelle la route POST /logout de FastAPI
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
