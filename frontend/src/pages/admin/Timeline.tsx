import { CalendarRange } from 'lucide-react';
import {useRef, useMemo, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import type { LoanTimelineEntry } from '@/client';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardBody } from '@/components/ui/Card';
import { DateRangeField } from '@/components/ui/DateRangeField';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { useLoanTimeline } from '@/hooks/useLoans';
import { formatDateShort, formatDayMonth } from '@/lib/format';
import { cn } from '@/lib/utils';
import dayjs, { Dayjs } from 'dayjs';

const DAY = 86_400_000;

interface DateRangeState {
  start: Dayjs | null;
  end: Dayjs | null;
}

function defaultRange() {
  const start = dayjs().startOf('day');
  const end = start.add(21, 'day');
  return { start, end };
}

const statusBar: Record<string, string> = {
  scheduled: 'bg-info/70 border-info',
  active: 'bg-success/70 border-success',
  returned: 'bg-ink-500 border-ink-400',
};

export function AdminTimelinePage() {
  const navigate = useNavigate();
  const [{ start, end }, setRange] = useState<DateRangeState>(defaultRange);
  const valid = !!start && !!end && start.isBefore(end);
  const startIso = valid ? start.toISOString() : '';
  const endIso = valid ? end.toISOString() : '';
  const { data, isLoading } = useLoanTimeline(startIso, endIso, valid);

  const cachedDataRef = useRef(data);

  if (data) {
    // eslint-disable-next-line react-hooks/refs
    cachedDataRef.current = data;
  }

  // eslint-disable-next-line react-hooks/refs
  const displayData = data || cachedDataRef.current;
  // eslint-disable-next-line react-hooks/refs
  const isInitialLoad = isLoading && !displayData;
  const windowStart = start ? start.valueOf() : 0;
  const windowEnd = end ? end.valueOf() : 0;
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
        label: formatDayMonth(dayjs(t).toISOString()),
      });
    }
    return marks;
  }, [windowStart, span]);

  const pos = (entry: LoanTimelineEntry) => {
    const s = dayjs(entry.actual_start_date ?? entry.start_date).valueOf();
    const e = dayjs(entry.actual_return_date ?? entry.end_date).valueOf();
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

      {/* eslint-disable-next-line react-hooks/refs */}
      {isInitialLoad ? (
        <Skeleton className="h-72 rounded-card" />
        // eslint-disable-next-line react-hooks/refs
      ) : !displayData || displayData.loans.length === 0 ? (
        <EmptyState
          icon={CalendarRange}
          title="Aucun prêt sur cette période"
          description="Ajustez les dates pour afficher les prêts planifiés ou en cours."
        />
      ) : (
        <Card>
          <CardBody className={cn("overflow-x-auto transition-opacity duration-200")}>
            <div className="min-w-160">
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
                {displayData.loans.map((entry) => {
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
