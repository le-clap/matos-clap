import { Check, X } from 'lucide-react';
import { useMemo, useState } from 'react';
import type { ItemPublic } from '@/client';
import { SearchInput } from '@/components/ui/SearchInput';
import { formatMoney } from '@/lib/format';
import { cn } from '@/lib/utils';

/**
 * Search-and-pick multiple inventory units.
 */
export function ItemMultiSelect({
  items,
  selected,
  onChange,
}: {
  items: ItemPublic[];
  selected: number[];
  onChange: (ids: number[]) => void;
}) {
  const [search, setSearch] = useState('');
  const selectedSet = new Set(selected);

  const itemById = useMemo(() => {
    const map = new Map<number, ItemPublic>();
    items.forEach((i) => map.set(i.id, i));
    return map;
  }, [items]);

  const matches = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return [];
    return items
      .filter((i) => i.name.toLowerCase().includes(q) || i.catalog.name.toLowerCase().includes(q))
      .slice(0, 8);
  }, [items, search]);

  const toggle = (id: number) =>
    onChange(selectedSet.has(id) ? selected.filter((x) => x !== id) : [...selected, id]);

  return (
    <div className="flex flex-col gap-3">
      <SearchInput
        value={search}
        onChange={setSearch}
        placeholder="Rechercher un article ou une référence…"
      />

      {search.trim() && (
        <div className="grid gap-2 sm:grid-cols-2">
          {matches.length === 0 ? (
            <p className="text-sm text-content-faint">Aucun article trouvé.</p>
          ) : (
            matches.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => toggle(item.id)}
                className={cn(
                  'flex items-center gap-3 rounded-lg border p-2.5 text-left transition-colors',
                  selectedSet.has(item.id)
                    ? 'border-primary/50 bg-danger-bg'
                    : 'border-border hover:border-border-strong hover:bg-surface-raised',
                )}
              >
                <div
                  className={cn(
                    'flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors',
                    selectedSet.has(item.id)
                      ? 'border-primary bg-primary text-white'
                      : 'border-border-strong',
                  )}
                >
                  {selectedSet.has(item.id) && <Check className="size-3.5" />}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{item.name}</p>
                  <p className="truncate text-[11px] text-content-faint">
                    {item.catalog.name}
                    {item.deposit_cents > 0 && ` · ${formatMoney(item.deposit_cents)}`}
                  </p>
                </div>
              </button>
            ))
          )}
        </div>
      )}

      {selected.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {selected.map((id) => (
            <span
              key={id}
              className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-danger-bg px-2.5 py-1 text-xs text-brand-200"
            >
              {itemById.get(id)?.name ?? `#${id}`}
              <button
                type="button"
                onClick={() => toggle(id)}
                className="text-brand-300/70 hover:text-brand-200"
                aria-label="Retirer"
              >
                <X className="size-3" />
              </button>
            </span>
          ))}
        </div>
      ) : (
        <p className="text-xs text-content-faint">Aucun article sélectionné.</p>
      )}
    </div>
  );
}
