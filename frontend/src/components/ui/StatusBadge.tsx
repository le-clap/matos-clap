import { Badge } from './Badge';

/** Loan lifecycle status. */
export function LoanStatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; tone: Parameters<typeof Badge>[0]['tone'] }> = {
    scheduled: { label: 'Planifié', tone: 'info' },
    active: { label: 'En cours', tone: 'success' },
    returned: { label: 'Rendu', tone: 'neutral' },
  };
  const cfg = map[status] ?? { label: status, tone: 'neutral' as const };
  return (
    <Badge tone={cfg.tone} dot>
      {cfg.label}
    </Badge>
  );
}

/** Item availability. */
export function AvailabilityBadge({ availability }: { availability: string }) {
  const map: Record<string, { label: string; tone: Parameters<typeof Badge>[0]['tone'] }> = {
    available: { label: 'Disponible', tone: 'success' },
    maintenance: { label: 'Maintenance', tone: 'warning' },
    retired: { label: 'Retiré', tone: 'neutral' },
  };
  const cfg = map[availability] ?? { label: availability, tone: 'neutral' as const };
  return <Badge tone={cfg.tone}>{cfg.label}</Badge>;
}

/** Physical condition. */
export function ConditionBadge({ condition }: { condition: string | null | undefined }) {
  if (!condition) return <span className="text-content-faint">—</span>;
  const map: Record<string, { label: string; tone: Parameters<typeof Badge>[0]['tone'] }> = {
    new: { label: 'Neuf', tone: 'success' },
    good: { label: 'Bon état', tone: 'info' },
    degraded: { label: 'Dégradé', tone: 'warning' },
  };
  const cfg = map[condition] ?? { label: condition, tone: 'neutral' as const };
  return <Badge tone={cfg.tone}>{cfg.label}</Badge>;
}

/** Request lifecycle: pending → accepted (loan) or refused. */
export function RequestStatusBadge({
  refused,
  loanId,
}: {
  refused?: boolean;
  loanId?: number | null;
}) {
  if (refused)
    return (
      <Badge tone="danger" dot>
        Refusée
      </Badge>
    );
  if (loanId != null)
    return (
      <Badge tone="success" dot>
        Acceptée
      </Badge>
    );
  return (
    <Badge tone="warning" dot>
      En attente
    </Badge>
  );
}
