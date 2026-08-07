import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

export function Pagination({
  page,
  limit,
  total,
  onPageChange,
}: {
  page: number;
  limit: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  const pageCount = Math.max(1, Math.ceil(total / limit));
  const from = total === 0 ? 0 : page * limit + 1;
  const to = Math.min((page + 1) * limit, total);

  if (total <= limit) return null;

  return (
    <div className="flex items-center justify-between gap-4 pt-1 text-sm text-content-muted">
      <span className="tabular-nums">
        {from}–{to} sur {total}
      </span>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="icon-sm"
          disabled={page <= 0}
          onClick={() => onPageChange(page - 1)}
          aria-label="Page précédente"
        >
          <ChevronLeft className="size-4" />
        </Button>
        <span className="tabular-nums">
          {page + 1} / {pageCount}
        </span>
        <Button
          variant="outline"
          size="icon-sm"
          disabled={page + 1 >= pageCount}
          onClick={() => onPageChange(page + 1)}
          aria-label="Page suivante"
        >
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
