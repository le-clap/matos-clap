import { PackageCheck, UserCheck } from 'lucide-react';
import type { ItemPublic } from '@/client';
import { Avatar } from '@/components/ui/Avatar';
import { EmptyState } from '@/components/ui/EmptyState';
import { Modal } from '@/components/ui/Modal';
import { Spinner } from '@/components/ui/Spinner';
import { AvailabilityBadge, ConditionBadge, LoanStatusBadge } from '@/components/ui/StatusBadge';
import { useItemHistory } from '@/hooks/useInventory';
import { formatDate } from '@/lib/format';

export function ItemHistoryModal({
  item,
  onClose,
}: {
  item: ItemPublic | null;
  onClose: () => void;
}) {
  const { data: entries, isLoading } = useItemHistory(item?.id ?? -1, !!item);

  const holder = entries?.find((e) => e.status === 'active')?.borrower.name ?? null;

  return (
    <Modal
      open={!!item}
      onClose={onClose}
      size="lg"
      title={item ? `Parcours · ${item.name}` : ''}
      description={item?.catalog.name}
    >
      {item && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <ConditionBadge condition={item.condition} />
          <AvailabilityBadge availability={item.availability} />
          {holder && (
            <span className="ml-auto text-sm text-content-muted">
              Actuellement chez <strong className="text-content">{holder}</strong>
            </span>
          )}
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-10">
          <Spinner />
        </div>
      ) : !entries || entries.length === 0 ? (
        <EmptyState
          icon={PackageCheck}
          title="Jamais prêté"
          description="Cet article n'a encore fait l'objet d'aucun prêt."
        />
      ) : (
        <ol className="relative">
          {entries.map((entry, i) => {
            const start = entry.actual_start_date ?? entry.start_date;
            const end = entry.actual_return_date ?? entry.end_date;
            const last = i === entries.length - 1;
            return (
              <li key={entry.loan_id} className="relative flex gap-4 pb-5 last:pb-0">
                {/* timeline rail */}
                <div className="flex flex-col items-center">
                  <Avatar name={entry.borrower.name} size="sm" />
                  {!last && <span className="mt-1 w-px flex-1 bg-border" />}
                </div>

                <div className="min-w-0 flex-1 pt-0.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium text-content">{entry.borrower.name}</span>
                    <LoanStatusBadge status={entry.status} />
                    {entry.return_condition && (
                      <ConditionBadge condition={entry.return_condition} />
                    )}
                  </div>
                  <p className="mt-1 text-sm text-content-muted">
                    du <strong>{formatDate(start)}</strong> au <strong>{formatDate(end)}</strong>
                    {!entry.actual_start_date && ' (prévu)'}
                  </p>
                  <p className="mt-0.5 flex items-center gap-1.5 text-xs text-content-faint">
                    <UserCheck className="size-3.5" />
                    Prêt #{entry.loan_id} · remis par {entry.assignee.name}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </Modal>
  );
}
