import { Minus, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

export function QuantityStepper({
  value,
  onChange,
  min = 1,
  max = 99,
  className,
}: {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-lg border border-border bg-surface',
        className,
      )}
    >
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={value <= min}
        className="flex size-9 items-center justify-center rounded-l-lg text-content-muted transition-colors hover:bg-surface-hover hover:text-content disabled:opacity-40"
        aria-label="Diminuer"
      >
        <Minus className="size-4" />
      </button>
      <span className="w-9 text-center text-sm font-medium tabular-nums">{value}</span>
      <button
        type="button"
        onClick={() => onChange(Math.min(max, value + 1))}
        disabled={value >= max}
        className="flex size-9 items-center justify-center rounded-r-lg text-content-muted transition-colors hover:bg-surface-hover hover:text-content disabled:opacity-40"
        aria-label="Augmenter"
      >
        <Plus className="size-4" />
      </button>
    </div>
  );
}
