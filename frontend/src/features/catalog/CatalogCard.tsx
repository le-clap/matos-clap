import { Check, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { CatalogPublic } from '@/client';
import { Button } from '@/components/ui/Button';
import { useCart } from '@/features/cart/CartContext';

export function CatalogThumb({
  imagePath,
  className = 'size-full',
}: {
  imagePath?: string | null;
  className?: string;
}) {
  return (
    <img
      src={imagePath || '/placeholder.jpg'}
      alt=""
      className={`${className} object-cover`}
      loading="lazy"
    />
  );
}

export function CatalogCard({ catalog }: { catalog: CatalogPublic }) {
  const { add, has } = useCart();
  const inCart = has(catalog.id);

  return (
    <div className="group flex flex-col overflow-hidden rounded-[var(--radius-card)] border border-border bg-surface transition-all hover:border-border-strong hover:shadow-card">
      <Link to={`/catalog/${catalog.id}`} className="relative aspect-[4/3] overflow-hidden">
        <CatalogThumb imagePath={catalog.image_path} />
        <span className="absolute left-2.5 top-2.5 rounded-full border border-border bg-ink-950/70 px-2 py-0.5 text-[11px] font-medium text-content-muted backdrop-blur">
          {catalog.category.name}
        </span>
      </Link>
      <div className="flex flex-1 flex-col p-3.5">
        <Link to={`/catalog/${catalog.id}`} className="min-w-0">
          <h3 className="truncate font-semibold text-content transition-colors group-hover:text-primary">
            {catalog.name}
          </h3>
        </Link>
        {catalog.description && (
          <p className="mt-1 line-clamp-2 text-[13px] text-content-muted">{catalog.description}</p>
        )}
        <Button
          size="sm"
          variant={inCart ? 'subtle' : 'secondary'}
          className="mt-3 w-full"
          onClick={() =>
            add({
              catalogId: catalog.id,
              name: catalog.name,
              imagePath: catalog.image_path,
            })
          }
        >
          {inCart ? (
            <>
              <Check className="size-4" /> Ajouté
            </>
          ) : (
            <>
              <Plus className="size-4" /> Ajouter
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
