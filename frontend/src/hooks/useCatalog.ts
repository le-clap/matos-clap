import { useQuery } from "@tanstack/react-query";
import type {CatalogPublic} from "@/client";
// import type {CatalogsGetCatalogsResponses} from "@/client";


const fetchCatalog = async (): Promise<CatalogPublic[]> => {
  const response = await fetch("/api/catalogs");
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
