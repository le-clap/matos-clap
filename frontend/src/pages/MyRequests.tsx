import { ClipboardList, Pencil, Phone, ScrollText, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { RequestPublic } from '@/client';
import { useAuth } from '@/auth/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { DateRangeField } from '@/components/ui/DateRangeField';
import { EmptyState } from '@/components/ui/EmptyState';
import { Field } from '@/components/ui/Field';
import { Input, Textarea } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { Skeleton } from '@/components/ui/Skeleton';
import { RequestStatusBadge } from '@/components/ui/StatusBadge';
import { useToast } from '@/components/ui/Toast';
import { useRequestMutations, useRequests } from '@/hooks/useRequests';
import { ApiError } from '@/lib/api';
import { formatDate, formatDateShort, isoToLocalInput, localInputToIso } from '@/lib/format';
import { PHONE_HINT, isValidPhone } from '@/lib/validation';

const LIMIT = 10;

export function MyRequestsPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(0);
  const { data, isLoading } = useRequests({
    borrowerId: user?.id,
    page,
    limit: LIMIT,
  });
  const [editing, setEditing] = useState<RequestPublic | null>(null);
  const [toDelete, setToDelete] = useState<RequestPublic | null>(null);
  const { update, remove } = useRequestMutations();
  const toast = useToast();

  return (
    <div>
      <PageHeader
        title="Mes demandes"
        description="Suivez l'état de vos demandes de prêt."
        action={
          <Button asChild>
            <Link to="/catalog">Nouvelle demande</Link>
          </Button>
        }
      />

      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-[var(--radius-card)]" />
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={ClipboardList}
          title="Aucune demande"
          description="Vous n'avez pas encore effectué de demande de prêt."
          action={
            <Button asChild>
              <Link to="/catalog">Parcourir le catalogue</Link>
            </Button>
          }
        />
      ) : (
        <div className="flex flex-col gap-3">
          {data.items.map((req) => {
            const pending = !req.processed && !req.refused;
            return (
              <Card key={req.id}>
                <CardBody className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <RequestStatusBadge refused={req.refused} loanId={req.loan_id} />
                      <span className="text-xs text-content-faint">
                        Demande #{req.id} · {formatDate(req.created_at)}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-content">
                      Du <strong>{formatDateShort(req.start_date)}</strong> au{' '}
                      <strong>{formatDateShort(req.end_date)}</strong>
                    </p>
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {req.requested_catalogs.map((rc) => (
                        <Badge key={rc.id} tone="neutral">
                          {rc.quantity}× {rc.catalog.name}
                        </Badge>
                      ))}
                    </div>
                    {req.reason && <p className="mt-2 text-sm text-content-muted">{req.reason}</p>}
                    {req.loan_id != null && (
                      <Link
                        to="/my/loans"
                        className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-brand-300 hover:underline"
                      >
                        <ScrollText className="size-4" />
                        Voir le prêt associé
                      </Link>
                    )}
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-3">
                    <div className="flex items-center gap-1.5 text-xs text-content-faint">
                      <Phone className="size-3.5" />
                      {req.phone_number}
                    </div>
                    {pending && (
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="sm" onClick={() => setEditing(req)}>
                          <Pencil className="size-4" /> Modifier
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          onClick={() => setToDelete(req)}
                          aria-label="Supprimer"
                          className="text-content-faint hover:text-brand-300"
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                </CardBody>
              </Card>
            );
          })}
          <Pagination page={page} limit={LIMIT} total={data.total} onPageChange={setPage} />
        </div>
      )}

      {editing && (
        <EditRequestModal
          request={editing}
          saving={update.isPending}
          onClose={() => setEditing(null)}
          onSave={async (body) => {
            await update.mutateAsync({ id: editing.id, body });
            toast.success('Demande mise à jour');
            setEditing(null);
          }}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        onClose={() => setToDelete(null)}
        loading={remove.isPending}
        title="Supprimer la demande ?"
        description="Cette demande sera définitivement supprimée."
        confirmLabel="Supprimer"
        onConfirm={async () => {
          try {
            await remove.mutateAsync(toDelete!.id);
            toast.success('Demande supprimée');
            setToDelete(null);
          } catch (err) {
            toast.error('Suppression impossible', err instanceof ApiError ? err.detail : undefined);
            setToDelete(null);
          }
        }}
      />
    </div>
  );
}

function EditRequestModal({
  request,
  onClose,
  onSave,
  saving,
}: {
  request: RequestPublic;
  onClose: () => void;
  onSave: (body: {
    phone_number: string;
    start_date: string;
    end_date: string;
    reason: string | null;
  }) => void;
  saving: boolean;
}) {
  const [phone, setPhone] = useState(request.phone_number);
  const [start, setStart] = useState(isoToLocalInput(request.start_date));
  const [end, setEnd] = useState(isoToLocalInput(request.end_date));
  const [reason, setReason] = useState(request.reason ?? '');

  const datesValid = !!start && !!end && new Date(start) < new Date(end);
  const phoneValid = isValidPhone(phone);

  return (
    <Modal
      open
      onClose={onClose}
      title="Modifier la demande"
      description="Vous pouvez modifier les dates, le téléphone et le motif tant que la demande est en attente."
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            disabled={!phoneValid || !datesValid}
            onClick={() =>
              onSave({
                phone_number: phone.trim(),
                start_date: localInputToIso(start),
                end_date: localInputToIso(end),
                reason: reason.trim() || null,
              })
            }
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <DateRangeField
          start={start}
          end={end}
          onStartChange={setStart}
          onEndChange={setEnd}
          required
        />
        <Field
          label="Téléphone"
          required
          hint={PHONE_HINT}
          error={phone && !phoneValid ? 'Numéro invalide' : null}
        >
          <Input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </Field>
        <Field label="Motif">
          <Textarea value={reason} onChange={(e) => setReason(e.target.value)} />
        </Field>
      </div>
    </Modal>
  );
}
