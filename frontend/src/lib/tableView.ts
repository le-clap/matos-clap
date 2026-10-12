import { useMemo, useState } from 'react';

type Value = string | number | null | undefined;
export type Sort<K extends string = string> = { key: K; dir: 'asc' | 'desc' };

const collator = new Intl.Collator('fr', { sensitivity: 'base', numeric: true });

const normalize = (s: string) => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();

function compareValues(a: Value, b: Value, sign: number) {
  if (a == null || a === '') return b == null || b === '' ? 0 : 1;
  if (b == null || b === '') return -1;
  if (typeof a === 'number' && typeof b === 'number') return (a - b) * sign;
  return collator.compare(String(a), String(b)) * sign;
}

export type ViewConfig<T, K extends string = string> = {
  searchText: (row: T) => string;
  sorters: Record<K, (row: T) => Value>;
  initial: Sort<NoInfer<K>>;
  tiebreak: readonly NoInfer<K>[];
};

export function useTableView<T extends { id: number }, K extends string>(
  rows: T[] | undefined,
  config: ViewConfig<T, K>,
) {
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<Sort<K>>(config.initial);

  const view = useMemo(() => {
    const { searchText, sorters, tiebreak } = config;
    const q = normalize(search.trim());
    const filtered = (rows ?? []).filter((r) => !q || normalize(searchText(r)).includes(q));
    const keys = [sort.key, ...tiebreak.filter((k) => k !== sort.key)];
    const sign = sort.dir === 'asc' ? 1 : -1;
    return filtered.sort((a, b) => {
      for (const [i, k] of keys.entries()) {
        const c = compareValues(sorters[k](a), sorters[k](b), i === 0 ? sign : 1);
        if (c) return c;
      }
      return a.id - b.id;
    });
  }, [rows, config, search, sort]);

  const toggle = (key: K) =>
    setSort((s) => ({ key, dir: s.key === key && s.dir === 'asc' ? 'desc' : 'asc' }));

  return { rows: view, search, setSearch, sort, toggle };
}
