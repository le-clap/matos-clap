import { CalendarRange } from 'lucide-react';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { LoanTimelineEntry } from '@/client';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardBody } from '@/components/ui/Card';
import { DateRangeField } from '@/components/ui/DateRangeField';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { useLoanTimeline } from '@/hooks/useLoans';
import { formatDateShort, formatDayMonth, isoToLocalInput, localInputToIso } from '@/lib/format';
import { cn } from '@/lib/utils';

const DAY = 86_400_000;

function defaultRange() {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const end = new Date(start.getTime() + 21 * DAY);
  return { start: isoToLocalInput(start.toISOString()), end: isoToLocalInput(end.toISOString()) };
}

const statusBar: Record<string, string> = {
  scheduled: 'bg-info/70 border-info',
  active: 'bg-success/70 border-success',
  returned: 'bg-ink-500 border-ink-400',
};

export function AdminTimelinePage() {
  const navigate = useNavigate();
  const [{ start, end }, setRange] = useState(defaultRange);
  const valid = !!start && !!end && new Date(start) < new Date(end);
  const startIso = valid ? localInputToIso(start) : '';
  const endIso = valid ? localInputToIso(end) : '';
  const { data, isLoading } = useLoanTimeline(startIso, endIso, valid);

  const windowStart = new Date(start).getTime();
  const windowEnd = new Date(end).getTime();
  const span = Math.max(1, windowEnd - windowStart);

  // Axis ticks — keep the count low (~8 max) so labels never overlap.
  const dayMarks = useMemo(() => {
    const days = Math.max(1, Math.round(span / DAY));
    const step = Math.max(1, Math.ceil(days / 8));
    const marks: { left: number; label: string }[] = [];
    for (let d = 0; d <= days; d += step) {
      const t = windowStart + d * DAY;
      marks.push({
        left: ((t - windowStart) / span) * 100,
        label: formatDayMonth(new Date(t).toISOString()),
      });
    }
    return marks;
  }, [windowStart, span]);

  const pos = (entry: LoanTimelineEntry) => {
    const s = new Date(entry.actual_start_date ?? entry.start_date).getTime();
    const e = new Date(entry.actual_return_date ?? entry.end_date).getTime();
    const left = Math.max(0, ((s - windowStart) / span) * 100);
    const right = Math.min(100, ((e - windowStart) / span) * 100);
    return { left, width: Math.max(1.5, right - left) };
  };

  return (
    <div>
      <PageHeader
        title="Planning"
        description="Visualisez les prêts qui se chevauchent sur une période."
      />

      <Card className="mb-5">
        <CardBody>
          <DateRangeField
            start={start}
            end={end}
            onStartChange={(v) => setRange((r) => ({ ...r, start: v }))}
            onEndChange={(v) => setRange((r) => ({ ...r, end: v }))}
            startLabel="Du"
            endLabel="Au"
          />
        </CardBody>
      </Card>

      {isLoading ? (
        <Skeleton className="h-72 rounded-[var(--radius-card)]" />
      ) : !data || data.loans.length === 0 ? (
        <EmptyState
          icon={CalendarRange}
          title="Aucun prêt sur cette période"
          description="Ajustez les dates pour afficher les prêts planifiés ou en cours."
        />
      ) : (
        <Card>
          <CardBody className="overflow-x-auto">
            <div className="min-w-[640px]">
              {/* Date axis */}
              <div className="relative mb-3 ml-44 h-5 border-b border-border">
                {dayMarks.map((m, i) => (
                  <span
                    key={i}
                    className="absolute -translate-x-1/2 text-[10px] text-content-faint"
                    style={{ left: `${m.left}%` }}
                  >
                    {m.label}
                  </span>
                ))}
              </div>

              <div className="flex flex-col gap-2">
                {data.loans.map((entry) => {
                  const { left, width } = pos(entry);
                  return (
                    <div key={entry.loan_id} className="flex items-center gap-3">
                      <div className="w-40 shrink-0 truncate text-right text-sm">
                        <span className="font-medium">{entry.borrower.name}</span>
                        <span className="block text-[11px] text-content-faint">
                          {entry.items.length} article(s)
                        </span>
                      </div>
                      <div className="relative h-9 flex-1 rounded-lg bg-surface-raised/50">
                        {dayMarks.map((m, i) => (
                          <span
                            key={i}
                            className="absolute top-0 h-full w-px bg-border/60"
                            style={{ left: `${m.left}%` }}
                          />
                        ))}
                        <button
                          onClick={() => navigate(`/admin/loans/${entry.loan_id}`)}
                          className={cn(
                            'absolute top-1 flex h-7 items-center overflow-hidden rounded-md border px-2 text-[11px] font-medium text-ink-950 transition-transform hover:scale-[1.01]',
                            statusBar[entry.status] ?? statusBar.returned,
                          )}
                          style={{ left: `${left}%`, width: `${width}%` }}
                          title={`${entry.borrower.name} · ${formatDateShort(entry.start_date)} → ${formatDateShort(entry.end_date)}`}
                        >
                          <span className="truncate">
                            {entry.items.map((it) => it.name).join(', ')}
                          </span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
