import { useQuery } from "@tanstack/react-query";
import type {CategoryPublic} from "@/client";


const fetchCategories = async (): Promise<CategoryPublic[]> => {
  const response = await fetch("/api/categories");
  if (!response.ok) {
    throw new Error("Erreur réseau");
  }
  return response.json();
};

export const useCategories = () => {
  return useQuery({
    queryKey: ["category", "full"], // clé unique pour le cache
    queryFn: fetchCategories,
    staleTime: 1000 * 60 * 5, // Cache de 5 min
  });
};
