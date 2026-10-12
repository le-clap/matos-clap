import { useMemo, useState } from 'react';

type Value = string | number | null | undefined;
export type Sorters<T> = Record<string, (row: T) => Value>;
export type Sort = { key: string; dir: 'asc' | 'desc' };

const collator = new Intl.Collator('fr', { sensitivity: 'base', numeric: true });

export const normalize = (s: string) => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();

function compareValues(a: Value, b: Value) {
  if (a == null || a === '') return b == null || b === '' ? 0 : 1; // empty values last
  if (b == null || b === '') return -1;
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  return collator.compare(String(a), String(b));
}

export type ViewConfig<T> = {
  searchText: (row: T) => string;
  sorters: Sorters<T>;
  initial: Sort;
  tiebreak: string[];
};

/**
 * Search + sort for a list. `config` must be a module-level constant so memoization holds.
 */
export function useTableView<T extends { id: number }>(
  rows: T[] | undefined,
  config: ViewConfig<T>,
) {
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<Sort>(config.initial);

  const view = useMemo(() => {
    const { searchText, sorters, tiebreak } = config;
    const q = normalize(search.trim());
    const filtered = (rows ?? []).filter((r) => !q || normalize(searchText(r)).includes(q));
    const keys = [sort.key, ...tiebreak.filter((k) => k !== sort.key)];
    const sign = sort.dir === 'asc' ? 1 : -1;
    return filtered.sort((a, b) => {
      for (const [i, k] of keys.entries()) {
        const c = compareValues(sorters[k](a), sorters[k](b));
        if (c) return i === 0 ? c * sign : c; // direction applies to the chosen column only
      }
      return a.id - b.id;
    });
  }, [rows, config, search, sort]);

  const toggle = (key: string) =>
    setSort((s) => ({ key, dir: s.key === key && s.dir === 'asc' ? 'desc' : 'asc' }));

  return { rows: view, search, setSearch, sort, toggle };
}
