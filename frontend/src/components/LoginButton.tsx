import { Button } from "@/components/ui/button";
import {Spinner} from "@/components/ui/spinner";
import {LogIn, LogOut} from 'lucide-react';

import {useAuth} from '@/contexts/AuthContext.tsx';

const LoginButton = () => {
  const {user, isLoading, login, logout} = useAuth();

  if (isLoading) return (
    <div>
      <Button>
        <Spinner/>
      </Button>
    </div>
  );

  if (user) return (
    <div className="logout-button">
      <Button onClick={logout} variant="outline" size="icon">
        <LogOut />
      </Button>
    </div>
  );

  return (
    <div className="login-button">
      <Button onClick={login} variant="outline" size="icon">
        <LogIn />
      </Button>
    </div>
  )
}

export default LoginButton;
