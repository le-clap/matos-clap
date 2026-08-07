import {
  CalendarRange,
  Pencil,
  PlayCircle,
  Trash2,
  Undo2,
  UserCheck,
  User as UserIcon,
} from 'lucide-react';
import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import type { Condition, ItemPublic, LoanedItemPublic, LoanPublic, UserBrief } from '@/client';
import { PageHeader } from '@/components/PageHeader';
import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { DateRangeField } from '@/components/ui/DateRangeField';
import { Field } from '@/components/ui/Field';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { PageSpinner } from '@/components/ui/Spinner';
import { ConditionBadge, LoanStatusBadge } from '@/components/ui/StatusBadge';
import { Table, TBody, Td, Th, THead, Tr } from '@/components/ui/Table';
import { useToast } from '@/components/ui/Toast';
import { ItemMultiSelect } from '@/features/loans/ItemMultiSelect';
import { UserCombobox } from '@/features/loans/UserCombobox';
import { useItems } from '@/hooks/useInventory';
import { useLoan, useLoanMutations } from '@/hooks/useLoans';
import { ApiError } from '@/lib/api';
import { formatDateTime, formatMoney, isoToLocalInput, localInputToIso } from '@/lib/format';
import { isOverdue } from '@/lib/loanStatus';

const CONDITIONS: { value: Condition; label: string }[] = [
  { value: 'new', label: 'Neuf' },
  { value: 'good', label: 'Bon état' },
  { value: 'degraded', label: 'Dégradé' },
];

export function AdminLoanDetailPage() {
  const { id } = useParams();
  const loanId = Number(id);
  const navigate = useNavigate();
  const toast = useToast();

  const { data: loan, isLoading } = useLoan(loanId);
  const { data: allItems } = useItems();
  const { update, returnLoan, partialReturn, remove } = useLoanMutations();

  const [modal, setModal] = useState<null | 'edit' | 'return' | 'partial'>(null);
  const [confirmStart, setConfirmStart] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  if (isLoading) return <PageSpinner />;
  if (!loan) {
    return <PageHeader title="Prêt introuvable" back={{ to: '/admin/loans', label: 'Prêts' }} />;
  }

  const status = loan.status;
  const overdue = isOverdue(loan);
  const outItems = loan.loaned_items.filter((li) => !li.actual_return_date);

  const startLoan = async () => {
    await update.mutateAsync({
      id: loan.id,
      body: { actual_start_date: new Date().toISOString() },
    });
    toast.success('Prêt démarré', 'Le matériel est marqué comme remis.');
    setConfirmStart(false);
  };

  return (
    <div>
      <PageHeader
        title={`Prêt #${loan.id}`}
        back={{ to: '/admin/loans', label: 'Prêts' }}
        action={
          <div className="flex flex-wrap items-center gap-2">
            {status === 'scheduled' && (
              <Button onClick={() => setConfirmStart(true)}>
                <PlayCircle className="size-4" /> Démarrer
              </Button>
            )}
            {status === 'active' && (
              <>
                <Button variant="secondary" onClick={() => setModal('partial')}>
                  Retour partiel
                </Button>
                <Button onClick={() => setModal('return')}>
                  <Undo2 className="size-4" /> Enregistrer le retour
                </Button>
              </>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setModal('edit')}
              aria-label="Modifier"
            >
              <Pencil className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setConfirmDelete(true)}
              aria-label="Supprimer"
            >
              <Trash2 className="size-4" />
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <Card>
          <CardHeader
            title="Matériel prêté"
            action={
              <div className="flex items-center gap-1.5">
                <LoanStatusBadge status={status} />
                {overdue && (
                  <Badge tone="danger" dot>
                    En retard
                  </Badge>
                )}
              </div>
            }
          />
          <Table className="rounded-none border-0">
            <THead>
              <Tr>
                <Th>Article</Th>
                <Th>État au retour</Th>
                <Th>Retour</Th>
              </Tr>
            </THead>
            <TBody>
              {loan.loaned_items.map((li) => (
                <Tr key={li.id}>
                  <Td className="font-medium">{li.item.name}</Td>
                  <Td>
                    <ConditionBadge condition={li.return_condition} />
                  </Td>
                  <Td>
                    {li.actual_return_date ? (
                      <span className="text-sm text-content-muted">
                        {formatDateTime(li.actual_return_date)}
                      </span>
                    ) : (
                      <Badge tone="info">En cours</Badge>
                    )}
                  </Td>
                </Tr>
              ))}
            </TBody>
          </Table>
        </Card>

        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader title="Détails" />
            <CardBody className="flex flex-col gap-3 text-sm">
              <Info icon={UserIcon} label="Emprunteur">
                <span className="flex items-center gap-2">
                  <Avatar name={loan.borrower.name} size="sm" /> {loan.borrower.name}
                </span>
              </Info>
              <Info icon={UserCheck} label="Responsable">
                {loan.assignee.name}
              </Info>
              <Info icon={CalendarRange} label="Période prévue">
                {formatDateTime(loan.start_date)}
                <br />→ {formatDateTime(loan.end_date)}
              </Info>
              {loan.actual_start_date && (
                <Info icon={PlayCircle} label="Début réel">
                  {formatDateTime(loan.actual_start_date)}
                </Info>
              )}
              {loan.actual_return_date && (
                <Info icon={Undo2} label="Retour réel">
                  {formatDateTime(loan.actual_return_date)}
                </Info>
              )}
              {loan.request_id && (
                <Info icon={CalendarRange} label="Demande liée">
                  <Link
                    to={`/admin/requests/${loan.request_id}`}
                    className="text-brand-300 hover:underline"
                  >
                    Demande #{loan.request_id}
                  </Link>
                </Info>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardBody className="flex items-center justify-between">
              <div>
                <p className="text-xs text-content-faint">Caution</p>
                <p className="text-lg font-semibold tabular-nums">
                  {formatMoney(loan.total_deposit_cents)}
                </p>
              </div>
              {loan.retained_deposit_cents != null && (
                <div className="text-right">
                  <p className="text-xs text-content-faint">Retenue</p>
                  <p className="text-lg font-semibold tabular-nums text-brand-300">
                    {formatMoney(loan.retained_deposit_cents)}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>

          {loan.comments && (
            <Card>
              <CardBody>
                <p className="text-xs text-content-faint">Commentaire</p>
                <p className="mt-1 text-sm text-content-muted">{loan.comments}</p>
              </CardBody>
            </Card>
          )}
        </div>
      </div>

      {modal === 'edit' && (
        <EditLoanModal
          loan={loan}
          scheduled={status === 'scheduled'}
          items={allItems ?? []}
          onClose={() => setModal(null)}
          onSave={async (body) => {
            try {
              await update.mutateAsync({ id: loan.id, body });
              toast.success('Prêt mis à jour');
              setModal(null);
            } catch (err) {
              toast.error(
                'Échec de la mise à jour',
                err instanceof ApiError ? err.detail : undefined,
              );
            }
          }}
          saving={update.isPending}
        />
      )}

      {modal === 'return' && (
        <ReturnModal
          loan={loan}
          items={outItems}
          onClose={() => setModal(null)}
          onSubmit={async (body) => {
            try {
              await returnLoan.mutateAsync({ id: loan.id, body });
              toast.success('Retour enregistré');
              setModal(null);
            } catch (err) {
              toast.error('Échec du retour', err instanceof ApiError ? err.detail : undefined);
            }
          }}
          saving={returnLoan.isPending}
        />
      )}

      {modal === 'partial' && (
        <PartialReturnModal
          items={outItems}
          onClose={() => setModal(null)}
          onSubmit={async (body) => {
            try {
              await partialReturn.mutateAsync({ id: loan.id, body });
              toast.success('Retour partiel enregistré');
              setModal(null);
            } catch (err) {
              toast.error('Échec', err instanceof ApiError ? err.detail : undefined);
            }
          }}
          saving={partialReturn.isPending}
        />
      )}

      <ConfirmDialog
        open={confirmStart}
        onClose={() => setConfirmStart(false)}
        onConfirm={startLoan}
        loading={update.isPending}
        tone="primary"
        title="Démarrer le prêt ?"
        description="Le matériel sera marqué comme remis à l'emprunteur dès maintenant."
        confirmLabel="Démarrer"
      />

      <ConfirmDialog
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        onConfirm={async () => {
          await remove.mutateAsync(loan.id);
          toast.success('Prêt supprimé');
          navigate('/admin/loans');
        }}
        loading={remove.isPending}
        title="Supprimer le prêt ?"
        description="Cette action est irréversible."
        confirmLabel="Supprimer"
      />
    </div>
  );
}

/* ------------------------------ Edit modal ------------------------------ */

interface EditLoanBody {
  borrower_id?: number;
  item_ids?: number[];
  start_date: string;
  end_date: string;
  total_deposit_cents: number;
  comments: string | null;
}

function EditLoanModal({
  loan,
  scheduled,
  items,
  onClose,
  onSave,
  saving,
}: {
  loan: LoanPublic;
  scheduled: boolean;
  items: ItemPublic[];
  onClose: () => void;
  onSave: (body: EditLoanBody) => void;
  saving: boolean;
}) {
  const [borrower, setBorrower] = useState<UserBrief | null>(loan.borrower);
  const [itemIds, setItemIds] = useState<number[]>(loan.loaned_items.map((li) => li.item.id));
  const [start, setStart] = useState(isoToLocalInput(loan.start_date));
  const [end, setEnd] = useState(isoToLocalInput(loan.end_date));
  const [deposit, setDeposit] = useState((loan.total_deposit_cents / 100).toFixed(2));
  const [comments, setComments] = useState(loan.comments ?? '');

  const datesValid = !!start && !!end && new Date(start) < new Date(end);

  return (
    <Modal
      open
      onClose={onClose}
      title="Modifier le prêt"
      description={scheduled ? "Le prêt n'a pas démarré." : 'Le prêt a démarré.'}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            disabled={!datesValid || (scheduled && (itemIds.length === 0 || !borrower))}
            onClick={() =>
              onSave({
                ...(scheduled
                  ? { borrower_id: (borrower ?? loan.borrower).id, item_ids: itemIds }
                  : {}),
                start_date: localInputToIso(start),
                end_date: localInputToIso(end),
                total_deposit_cents: Math.round(parseFloat(deposit || '0') * 100),
                comments: comments.trim() || null,
              })
            }
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        {scheduled && (
          <>
            <Field label="Emprunteur">
              <UserCombobox value={borrower} onChange={setBorrower} />
            </Field>
            <Field label="Matériel">
              <ItemMultiSelect items={items} selected={itemIds} onChange={setItemIds} />
            </Field>
          </>
        )}
        <DateRangeField start={start} end={end} onStartChange={setStart} onEndChange={setEnd} />
        <Field label="Caution (€)">
          <Input
            type="number"
            min="0"
            step="0.01"
            value={deposit}
            onChange={(e) => setDeposit(e.target.value)}
          />
        </Field>
        <Field label="Commentaire">
          <Textarea value={comments} onChange={(e) => setComments(e.target.value)} />
        </Field>
      </div>
    </Modal>
  );
}

/* ----------------------------- Return modal ----------------------------- */

function ReturnModal({
  loan,
  items,
  onClose,
  onSubmit,
  saving,
}: {
  loan: LoanPublic;
  items: LoanedItemPublic[];
  onClose: () => void;
  onSubmit: (body: {
    retained_deposit_cents: number;
    item_return_conditions: { item_id: number; return_condition: Condition }[];
    comments: string | null;
  }) => void;
  saving: boolean;
}) {
  const [retained, setRetained] = useState('0.00');
  const [conditions, setConditions] = useState<Record<number, Condition>>(() =>
    Object.fromEntries(items.map((li) => [li.item.id, 'good' as Condition])),
  );
  const [comments, setComments] = useState('');

  return (
    <Modal
      open
      onClose={onClose}
      title="Enregistrer le retour"
      description="Renseignez l'état du matériel et la caution éventuellement retenue."
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            onClick={() =>
              onSubmit({
                retained_deposit_cents: Math.round(parseFloat(retained || '0') * 100),
                item_return_conditions: items.map((li) => ({
                  item_id: li.item.id,
                  return_condition: conditions[li.item.id] ?? 'good',
                })),
                comments: comments.trim() || null,
              })
            }
          >
            Confirmer le retour
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          {items.map((li) => (
            <div
              key={li.id}
              className="flex items-center justify-between gap-3 rounded-lg border border-border bg-surface-raised/40 p-2.5"
            >
              <span className="text-sm font-medium">{li.item.name}</span>
              <Select
                className="w-40"
                value={conditions[li.item.id] ?? 'good'}
                onChange={(e) =>
                  setConditions((prev) => ({
                    ...prev,
                    [li.item.id]: e.target.value as Condition,
                  }))
                }
              >
                {CONDITIONS.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </Select>
            </div>
          ))}
        </div>
        <Field
          label="Caution retenue (€)"
          hint={`Caution totale : ${formatMoney(loan.total_deposit_cents)}`}
        >
          <Input
            type="number"
            min="0"
            step="0.01"
            value={retained}
            onChange={(e) => setRetained(e.target.value)}
          />
        </Field>
        <Field label="Commentaire">
          <Textarea value={comments} onChange={(e) => setComments(e.target.value)} />
        </Field>
      </div>
    </Modal>
  );
}

/* ------------------------- Partial return modal ------------------------- */

function PartialReturnModal({
  items,
  onClose,
  onSubmit,
  saving,
}: {
  items: LoanedItemPublic[];
  onClose: () => void;
  onSubmit: (body: { items: { item_id: number; return_condition: Condition }[] }) => void;
  saving: boolean;
}) {
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [conditions, setConditions] = useState<Record<number, Condition>>({});
  const tooMany = selected.size >= items.length;

  return (
    <Modal
      open
      onClose={onClose}
      title="Retour partiel"
      description="Sélectionnez les articles rendus. Au moins un doit rester en cours."
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            disabled={selected.size === 0 || tooMany}
            onClick={() =>
              onSubmit({
                items: [...selected].map((itemId) => ({
                  item_id: itemId,
                  return_condition: conditions[itemId] ?? 'good',
                })),
              })
            }
          >
            Valider le retour partiel
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-2">
        {items.map((li) => {
          const checked = selected.has(li.item.id);
          return (
            <div
              key={li.id}
              className="flex items-center gap-3 rounded-lg border border-border bg-surface-raised/40 p-2.5"
            >
              <label className="flex flex-1 items-center gap-2.5 text-sm font-medium">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() =>
                    setSelected((prev) => {
                      const next = new Set(prev);
                      if (next.has(li.item.id)) next.delete(li.item.id);
                      else next.add(li.item.id);
                      return next;
                    })
                  }
                  className="size-4 accent-[var(--color-primary)]"
                />
                {li.item.name}
              </label>
              {checked && (
                <Select
                  className="w-40"
                  value={conditions[li.item.id] ?? 'good'}
                  onChange={(e) =>
                    setConditions((prev) => ({
                      ...prev,
                      [li.item.id]: e.target.value as Condition,
                    }))
                  }
                >
                  {CONDITIONS.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </Select>
              )}
            </div>
          );
        })}
      </div>
      {tooMany && (
        <p className="mt-3 text-sm text-warning">
          Pour un retour total, utilisez « Enregistrer le retour ».
        </p>
      )}
    </Modal>
  );
}

function Info({
  icon: Icon,
  label,
  children,
}: {
  icon: typeof UserIcon;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-content-faint" />
      <div className="min-w-0 flex-1">
        <p className="text-xs text-content-faint">{label}</p>
        <div className="mt-0.5 text-content">{children}</div>
      </div>
    </div>
  );
}
