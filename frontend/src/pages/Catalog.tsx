import { PackageSearch } from 'lucide-react';
import { useMemo, useState } from 'react';
import type { CatalogPublic } from '@/client';
import { PageHeader } from '@/components/PageHeader';
import { EmptyState } from '@/components/ui/EmptyState';
import { SearchInput } from '@/components/ui/SearchInput';
import { Skeleton } from '@/components/ui/Skeleton';
import { CatalogCard } from '@/features/catalog/CatalogCard';
import { useCatalogs, useCategories } from '@/hooks/useInventory';
import { useTableView, type ViewConfig } from '@/lib/tableView';
import { cn } from '@/lib/utils';

const CATALOG_VIEW: ViewConfig<CatalogPublic> = {
  searchText: (c) => `${c.name} ${c.description ?? ''} ${c.category.name}`,
  sorters: { name: (c) => c.name, category: (c) => c.category.name },
  initial: { key: 'category', dir: 'asc' },
  tiebreak: ['category', 'name'],
};

export function CatalogPage() {
  const { data: catalogs, isLoading } = useCatalogs();
  const { data: categories } = useCategories();
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const inCategory = useMemo(
    () => catalogs?.filter((c) => categoryId === null || c.category.id === categoryId),
    [catalogs, categoryId],
  );
  const { rows: filtered, search, setSearch } = useTableView(inCategory, CATALOG_VIEW);

  return (
    <div>
      <PageHeader
        title="Catalogue"
        description="Parcourez le matériel disponible et ajoutez-le à votre demande de prêt."
      />

      <div className="mb-5 flex flex-col gap-3">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Rechercher un appareil, une catégorie…"
          className="max-w-md"
        />
        {categories && categories.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <Chip active={categoryId === null} onClick={() => setCategoryId(null)}>
              Tout
            </Chip>
            {categories.map((cat) => (
              <Chip
                key={cat.id}
                active={categoryId === cat.id}
                onClick={() => setCategoryId(cat.id)}
              >
                {cat.name}
              </Chip>
            ))}
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="aspect-[3/4] rounded-[var(--radius-card)]" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={PackageSearch}
          title="Aucun résultat"
          description={
            search || categoryId !== null
              ? 'Aucun matériel ne correspond à votre recherche.'
              : 'Le catalogue est vide pour le moment.'
          }
        />
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {filtered.map((catalog) => (
            <CatalogCard key={catalog.id} catalog={catalog} />
          ))}
        </div>
      )}
    </div>
  );
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'rounded-full border px-3.5 py-1.5 text-[13px] font-medium transition-colors',
        active
          ? 'border-primary/40 bg-danger-bg text-brand-200'
          : 'border-border text-content-muted hover:border-border-strong hover:text-content',
      )}
    >
      {children}
    </button>
  );
}
