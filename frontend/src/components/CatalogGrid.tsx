import type {CatalogItem} from "@/types/CatalogItem.ts";
import clapLogo from "@/assets/logos/Logo CLAP.png";
import type {FC} from "react";

import {
  Item,
  ItemContent,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import {Spinner} from "@/components/ui/spinner.tsx";

export interface CatalogGridProps {
  items: CatalogItem[] | undefined;
  isLoading: boolean;
  error?: Error;
}

const CatalogGrid: FC<CatalogGridProps> = ({
                                             items,
                                             isLoading,
                                             error
                                           }) => {
  if (isLoading) return (
    <div className="text-zinc-400">
      <Item>
        <ItemMedia>
          <Spinner/>
        </ItemMedia>
        <ItemContent>
          <ItemTitle className="line-clamp-1">Chargement du matériel...</ItemTitle>
        </ItemContent>
      </Item>
    </div>
  )

  if (error) return <div className="text-red-500">{error.message}</div>

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {/* Boucle pour afficher les items */}
      {items?.map((item: CatalogItem) => (
        <div key={item.id} className="flex flex-col bg-zinc-800 p-4 rounded-lg text-white gap-3 justify-between">
          <h2 className="text-xl font-bold">{item.label}</h2>
          <p className="text-gray-400">{item.description}</p>
          {item.image_path ? (
            <img src={item.image_path} alt={"Photo"}
                 className="aspect-square border-2 border-white object-cover rounded-2xl "/>
          ) : (
            <img src={clapLogo} alt={"Logo CLAP"} className="aspect-square"/>
          )}
        </div>
      ))}
    </div>
  )
}

export default CatalogGrid;