import { ArrowDown, ArrowUp, ChevronsUpDown } from 'lucide-react';
import { type HTMLAttributes, type TdHTMLAttributes, type ThHTMLAttributes } from 'react';
import type { Sort } from '@/lib/tableView';
import { cn } from '@/lib/utils';

export function Table({ className, ...props }: HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="w-full overflow-x-auto rounded-[var(--radius-card)] border border-border bg-surface">
      <table className={cn('w-full border-collapse text-sm', className)} {...props} />
    </div>
  );
}

export function THead({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead className={cn('border-b border-border bg-surface-raised/50', className)} {...props} />
  );
}

export function TBody(props: HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody {...props} />;
}

export function Tr({ className, ...props }: HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={cn(
        'border-b border-border last:border-0 transition-colors hover:bg-surface-raised/40',
        className,
      )}
      {...props}
    />
  );
}

export function Th({ className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn(
        'px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-content-faint',
        className,
      )}
      {...props}
    />
  );
}

export function Td({ className, ...props }: TdHTMLAttributes<HTMLTableCellElement>) {
  return <td className={cn('px-4 py-3 align-middle text-content', className)} {...props} />;
}

/** Clickable header cell for column `k` of a `useTableView` view. */
export function SortTh({
  children,
  view,
  k,
  className,
}: {
  children: React.ReactNode;
  view: { sort: Sort; toggle: (key: string) => void };
  k: string;
  className?: string;
}) {
  const dir = view.sort.key === k ? view.sort.dir : undefined;
  const Icon = dir === 'asc' ? ArrowUp : dir === 'desc' ? ArrowDown : ChevronsUpDown;
  return (
    <Th
      className={className}
      aria-sort={dir === 'asc' ? 'ascending' : dir === 'desc' ? 'descending' : 'none'}
    >
      <button
        onClick={() => view.toggle(k)}
        className={cn(
          'inline-flex items-center gap-1 uppercase tracking-wide transition-colors hover:text-content',
          dir && 'text-content',
        )}
      >
        {children}
        <Icon className={cn('size-3.5', !dir && 'opacity-40')} />
      </button>
    </Th>
  );
}
