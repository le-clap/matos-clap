import { useQuery } from "@tanstack/react-query";
import type {CatalogItem} from "@/types/CatalogItem.ts";

const fetchCatalog = async (): Promise<CatalogItem[]> => {
  const response = await fetch("/api/catalog");
  if (!response.ok) {
    throw new Error("Erreur réseau");
  }
  return response.json();
};

export const useCatalog = () => {
  return useQuery({
    queryKey: ["catalog", "full"], // clé unique pour le cache
    queryFn: fetchCatalog,
    staleTime: 1000 * 60 * 5, // Cache de 5 min
  });
};