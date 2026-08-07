import { ArrowRight } from 'lucide-react';
import { Field } from './Field';
import { Input } from './Input';
import { cn } from '@/lib/utils';

/**
 * Two `datetime-local` inputs for a [start, end] window. Values are raw
 * datetime-local strings; convert with `localInputToIso` before sending.
 *
 * Pass `stack` in narrow containers (e.g. a sidebar column) so the two inputs
 * stack vertically instead of overflowing.
 */
export function DateRangeField({
  start,
  end,
  onStartChange,
  onEndChange,
  startLabel = 'Début',
  endLabel = 'Fin',
  required,
  error,
  stack = false,
}: {
  start: string;
  end: string;
  onStartChange: (value: string) => void;
  onEndChange: (value: string) => void;
  startLabel?: string;
  endLabel?: string;
  required?: boolean;
  error?: string | null;
  stack?: boolean;
}) {
  return (
    <div className="flex flex-col gap-2">
      <div className={cn('flex flex-col gap-3', !stack && 'sm:flex-row sm:items-end')}>
        <Field label={startLabel} required={required} className="min-w-0 flex-1">
          <Input
            type="datetime-local"
            value={start}
            onChange={(e) => onStartChange(e.target.value)}
            className="min-w-0"
          />
        </Field>
        {!stack && (
          <ArrowRight className="hidden size-4 shrink-0 -translate-y-2.5 text-content-faint sm:block" />
        )}
        <Field label={endLabel} required={required} className="min-w-0 flex-1">
          <Input
            type="datetime-local"
            value={end}
            min={start || undefined}
            onChange={(e) => onEndChange(e.target.value)}
            className="min-w-0"
          />
        </Field>
      </div>
      {error && <p className="text-xs text-brand-300">{error}</p>}
    </div>
  );
}
