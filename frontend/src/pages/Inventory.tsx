import {useCatalog} from "@/hooks/useCatalog.ts";

import CatalogGrid from "@/components/CatalogGrid.tsx";
// import {SearchBar} from "@/components/SearchBar.tsx";

const Inventory = () => {

    const {data: allItems, isLoading} = useCatalog();

    return (
      // Padding TOP pour rester en dessous du menu (à voir si on encapsule le menu dans header pour éviter d'avoir à faire ça)
      <div className="min-h-screen bg-[#1a1a1a] pt-40 px-4 md:px-8 pb-20">

        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-heading text-white mb-6 pb-2 border-b border-teal-800">Inventaire</h1>

          <div className="inventory-container flex flex-col gap-3">
            <div className="filter-bar flex justify-center">
              Barre de recherche et classements (WIP)
            </div>
            <div className="grid-filters-container flex flex-row gap-3 ">
              <div className="filters flex flex-col items-start">
                Filtres (WIP)
              </div>
              <div className="catalog-grid flex">
                <CatalogGrid
                  items={allItems}
                  isLoading={isLoading}
                />
              </div>
            </div>
          </div>

        </div>

      </div>
    );
  }
;

export default Inventory;