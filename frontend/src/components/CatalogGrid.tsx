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
    <div className="text-muted-foreground">
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

  if (error) return <div className="text-destructive">{error.message}</div>

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
      {/* Boucle pour afficher les items */}
      {items?.map((item: CatalogItem) => (
        <div key={item.id} className="flex flex-col bg-secondary text-secondary-foreground p-4 rounded-lg gap-3 justify-between">
          <h2 className="text-xl font-bold">{item.name}</h2>
          <p className="text-muted-foreground">{item.description}</p>
          {item.image_path ? (
            <img src={item.image_path} alt={"Photo"}
                 className="aspect-square object-cover rounded-2xl "/>
          ) : (
            <img src={clapLogo} alt={"Logo CLAP"} className="aspect-square"/>
          )}
        </div>
      ))}
    </div>
  )
}

export default CatalogGrid;