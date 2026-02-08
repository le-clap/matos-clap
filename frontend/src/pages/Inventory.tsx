import {useEffect, useState} from "react";
import type {CatalogItem} from "@/types/CatalogItem.ts";

const Inventory = () => {

    const [items, setItem] = useState<CatalogItem[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // Peut-être réfléchir à implémenter Axios plus tard

    useEffect(() => {
        const fetchCatalogItem = async () => {
          try {
            const response = await fetch('http://localhost:8000/api/catalog');

            if (!response.ok) {
              throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();
            setItem(data);
          } catch (err) {
            console.log(err);
            setError("Impossible de charger le catalogue. Voir les logs pour plus d'info");
          } finally {
            setLoading(false);
          }
        };
        fetchCatalogItem().then(r => console.log(r));
      }, []
    );


    return (
      // Padding TOP pour rester en dessous du menu (à voir si on encapsule le menu dans header pour éviter d'avoir à faire ça)
      <div className="min-h-screen bg-[#1a1a1a] pt-40 px-4 md:px-8">

        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-heading text-white mb-8">Inventaire</h1>

          {/* Affichage conditionnel */}
          {loading && <div className="text-zinc-500">Chargement du matériel...</div>}

          {error && <div className="text-red-500">{error}</div>}

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {/* Boucle pour afficher les items */}
            {items && items.map((item) => (
              <div key={item.id} className="flex flex-col bg-zinc-800 p-4 rounded-lg text-white gap-3 justify-between">
                <h2 className="text-xl font-bold">{item.label}</h2>
                <p className="text-gray-400">{item.description}</p>
                <img src={item.image_path} alt={"Photo"} className="aspect-square object-cover rounded-2xl "/>
              </div>
            ))}
          </div>
        </div>

      </div>
    );
  }
;

export default Inventory;