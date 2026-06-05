import React from "react";
import {useNavigate} from "react-router-dom";

export const useHandleNavigation = () => {
  const navigate = useNavigate();

  return (path: string) => (e: React.MouseEvent) => {
    if (path.startsWith('/')) {
      e.preventDefault(); // Bloque le rechargement
      navigate(path);     // Redirection SPA
      window.scrollTo(0, 0);
    }
  };
};
