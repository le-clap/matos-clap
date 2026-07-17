import {
  Ban,
  CalendarRange,
  Check,
  CheckCircle2,
  Phone,
  RotateCcw,
  ScrollText,
  Search,
  TriangleAlert,
  User as UserIcon,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import type {
  ItemPublic,
  RequestPublic,
  RequestRecommendationItem,
  RequestRecommendationsResponse,
} from "@/client";
import { PageHeader } from "@/components/PageHeader";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { DateRangeField } from "@/components/ui/DateRangeField";
import { Field } from "@/components/ui/Field";
import { Input, Textarea } from "@/components/ui/Input";
import { PageSpinner } from "@/components/ui/Spinner";
import { RequestStatusBadge } from "@/components/ui/StatusBadge";
import { useToast } from "@/components/ui/Toast";
import { useItems } from "@/hooks/useInventory";
import { useLoanMutations } from "@/hooks/useLoans";
import {
  useRequest,
  useRequestMutations,
  useRequestRecommendations,
} from "@/hooks/useRequests";
import { ApiError } from "@/lib/api";
import {
  formatDateShort,
  formatMoney,
  isoToLocalInput,
  localInputToIso,
} from "@/lib/format";
import { cn } from "@/lib/utils";

export function AdminRequestDetailPage() {
  const { id } = useParams();
  const requestId = Number(id);
  const navigate = useNavigate();
  const toast = useToast();

  const { data: request, isLoading } = useRequest(requestId);
  const { data: recs, isLoading: recsLoading } =
    useRequestRecommendations(requestId);
  const { data: items } = useItems();
  const { remove, setStatus } = useRequestMutations();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const pending = !request?.processed && !request?.refused;

  if (isLoading) return <PageSpinner />;
  if (!request) {
    return (
      <PageHeader
        title="Demande introuvable"
        back={{ to: "/admin/requests", label: "Demandes" }}
      />
    );
  }

  return (
    <div>
      <PageHeader
        title={`Demande #${request.id}`}
        back={{ to: "/admin/requests", label: "Demandes" }}
        action={
          <>
            <RequestStatusBadge refused={request.refused} loanId={request.loan_id} />
            {pending && (
              <Button
                variant="secondary"
                size="sm"
                loading={setStatus.isPending}
                onClick={async () => {
                  await setStatus.mutateAsync({id: request.id, status: "refused"});
                  toast.toast({ tone: "info", title: "Demande refusée" });
                }}
              >
                <Ban className="size-4" /> Refuser
              </Button>
            )}
            <Button
              variant="danger"
              size="sm"
              onClick={() => setConfirmDelete(true)}
            >
              Supprimer
            </Button>
          </>
        }
      />

      {request.refused ? (
        <RefusedNotice
          request={request}
          reopening={setStatus.isPending}
          onReopen={async () => {
            await setStatus.mutateAsync({id: request.id, status: "pending"});
            toast.success("Demande rouverte", "Elle est de nouveau en attente.");
          }}
        />
      ) : request.loan_id != null ? (
        <ProcessedNotice request={request} />
      ) : recsLoading || !recs ? (
        <PageSpinner label="Calcul des recommandations…" />
      ) : (
        <Workspace
          request={request}
          recs={recs}
          items={items ?? []}
          onCreated={(loanId) => navigate(`/admin/loans/${loanId}`)}
        />
      )}

      <ConfirmDialog
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        onConfirm={async () => {
          await remove.mutateAsync(request.id);
          toast.success("Demande supprimée");
          navigate("/admin/requests");
        }}
        loading={remove.isPending}
        title="Supprimer la demande ?"
        description="Cette action est irréversible."
        confirmLabel="Supprimer"
      />
    </div>
  );
}

/** Shown when the request has already been turned into a loan. */
function ProcessedNotice({ request }: { request: RequestPublic }) {
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <Card>
        <CardBody className="flex flex-col items-center gap-4 py-12 text-center">
          <div className="flex size-12 items-center justify-center rounded-full bg-success-bg text-success">
            <CheckCircle2 className="size-6" />
          </div>
          <div>
            <h3 className="font-semibold">Demande traitée</h3>
            <p className="mt-1 max-w-sm text-sm text-content-muted">
              Cette demande a déjà été transformée en prêt. Il n'est plus
              possible d'en créer un second.
            </p>
          </div>
          <Link
            to={`/admin/loans/${request.loan_id}`}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-300 hover:underline"
          >
            <ScrollText className="size-4" />
            Voir le prêt #{request.loan_id}
          </Link>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Informations" />
        <CardBody className="flex flex-col gap-3 text-sm">
          <InfoRow icon={UserIcon} label="Demandeur">
            <div className="flex items-center gap-2">
              <Avatar name={request.borrower.name} size="sm" />
              {request.borrower.name}
            </div>
          </InfoRow>
          <InfoRow icon={Phone} label="Téléphone">
            {request.phone_number}
          </InfoRow>
          <InfoRow icon={CalendarRange} label="Période souhaitée">
            {formatDateShort(request.start_date)} →{" "}
            {formatDateShort(request.end_date)}
          </InfoRow>
        </CardBody>
      </Card>
    </div>
  );
}

/** Shown when the request has been refused. */
function RefusedNotice({
  request,
  onReopen,
  reopening,
}: {
  request: RequestPublic;
  onReopen: () => void;
  reopening: boolean;
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <Card>
        <CardBody className="flex flex-col items-center gap-4 py-12 text-center">
          <div className="flex size-12 items-center justify-center rounded-full bg-danger-bg text-brand-400">
            <Ban className="size-6" />
          </div>
          <div>
            <h3 className="font-semibold">Demande refusée</h3>
            <p className="mt-1 max-w-sm text-sm text-content-muted">
              Cette demande a été refusée. Vous pouvez la rouvrir pour la
              remettre en attente et éventuellement créer un prêt.
            </p>
          </div>
          <Button variant="secondary" loading={reopening} onClick={onReopen}>
            <RotateCcw className="size-4" />
            Rouvrir la demande
          </Button>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Informations" />
        <CardBody className="flex flex-col gap-3 text-sm">
          <InfoRow icon={UserIcon} label="Demandeur">
            <div className="flex items-center gap-2">
              <Avatar name={request.borrower.name} size="sm" />
              {request.borrower.name}
            </div>
          </InfoRow>
          <InfoRow icon={Phone} label="Téléphone">
            {request.phone_number}
          </InfoRow>
          <InfoRow icon={CalendarRange} label="Période souhaitée">
            {formatDateShort(request.start_date)} →{" "}
            {formatDateShort(request.end_date)}
          </InfoRow>
        </CardBody>
      </Card>
    </div>
  );
}

/**
 * Interactive create-loan workspace. Mounted only once the request and its
 * recommendations are loaded, so all state initializes directly from props.
 */
function Workspace({
  request,
  recs,
  items,
  onCreated,
}: {
  request: RequestPublic;
  recs: RequestRecommendationsResponse;
  items: ItemPublic[];
  onCreated: (loanId: number) => void;
}) {
  const toast = useToast();
  const { create } = useLoanMutations();

  const [selected, setSelected] = useState<Set<number>>(
    () => new Set(recs.recommendations.flatMap((r) => r.recommended_item_ids)),
  );
  const [start, setStart] = useState(() => isoToLocalInput(request.start_date));
  const [end, setEnd] = useState(() => isoToLocalInput(request.end_date));
  const [depositOverride, setDepositOverride] = useState<string | null>(null);
  const [comments, setComments] = useState("");
  const [error, setError] = useState<string | null>(null);

  const [itemSearch, setItemSearch] = useState("");

  const depositByItem = useMemo(() => {
    const map = new Map<number, number>();
    items.forEach((i) => map.set(i.id, i.deposit_cents));
    return map;
  }, [items]);

  const itemById = useMemo(() => {
    const map = new Map<number, ItemPublic>();
    items.forEach((i) => map.set(i.id, i));
    return map;
  }, [items]);

  // Items that are NOT among the recommendation candidates — the CLAP can still
  // add any of them to the loan (e.g. a substitute or an extra accessory).
  const candidateIds = useMemo(
    () =>
      new Set(
        recs.recommendations.flatMap((r) =>
          r.candidate_items.map((c) => c.item_id),
        ),
      ),
    [recs],
  );

  const extraSelected = useMemo(
    () => [...selected].filter((id) => !candidateIds.has(id)),
    [selected, candidateIds],
  );

  const extraMatches = useMemo(() => {
    const q = itemSearch.trim().toLowerCase();
    if (!q) return [];
    return items
      .filter(
        (i) =>
          !i.deleted_at &&
          !candidateIds.has(i.id) &&
          (i.name.toLowerCase().includes(q) ||
            i.catalog.name.toLowerCase().includes(q)),
      )
      .slice(0, 8);
  }, [items, candidateIds, itemSearch]);

  const suggestedDeposit = useMemo(
    () => [...selected].reduce((sum, id) => sum + (depositByItem.get(id) ?? 0), 0),
    [selected, depositByItem],
  );

  const depositValue =
    depositOverride ?? (suggestedDeposit / 100).toFixed(2);

  const toggle = (itemId: number) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) next.delete(itemId);
      else next.add(itemId);
      return next;
    });

  const datesValid = !!start && !!end && new Date(start) < new Date(end);

  const submit = async () => {
    setError(null);
    if (selected.size === 0) return setError("Sélectionnez au moins un article.");
    if (!datesValid) return setError("Période invalide.");
    try {
      const res = await create.mutateAsync({
        borrower_id: request.borrower.id,
        start_date: localInputToIso(start),
        end_date: localInputToIso(end),
        item_ids: [...selected],
        total_deposit_cents: Math.round(parseFloat(depositValue || "0") * 100),
        request_id: request.id,
        comments: comments.trim() || null,
      });
      if (res.warnings.length > 0) {
        toast.toast({
          tone: "warning",
          title: "Prêt créé avec avertissements",
          description: res.warnings.map((w) => w.message).join(" · "),
        });
      } else {
        toast.success("Prêt créé", "La demande a été marquée comme traitée.");
      }
      onCreated(res.loan.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail ?? err.message : "Erreur");
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="flex flex-col gap-6">
      <Card>
        <CardHeader
          title="Sélection du matériel"
          description="Cochez les articles à inclure. Les recommandations du système sont pré-sélectionnées."
        />
        <CardBody className="flex flex-col gap-5">
          {recs.recommendations.map((rec) => (
            <div key={rec.requested_catalog_id}>
              <div className="mb-2 flex items-center justify-between">
                <h4 className="font-medium">
                  {rec.catalog.name}
                  <span className="ml-2 text-sm font-normal text-content-faint">
                    {rec.requested_quantity} demandé(s)
                  </span>
                </h4>
                <span className="text-xs text-content-faint">
                  {rec.candidate_items.length} candidat(s)
                </span>
              </div>
              {(rec.warnings ?? []).map((w, i) => (
                <p
                  key={i}
                  className="mb-2 flex items-center gap-1.5 rounded-lg border border-warning/30 bg-warning-bg px-2.5 py-1.5 text-xs text-warning"
                >
                  <TriangleAlert className="size-3.5" /> {w}
                </p>
              ))}
              <div className="grid gap-2 sm:grid-cols-2">
                {rec.candidate_items.map((item) => (
                  <CandidateItem
                    key={item.item_id}
                    item={item}
                    deposit={depositByItem.get(item.item_id)}
                    selected={selected.has(item.item_id)}
                    onToggle={() => toggle(item.item_id)}
                  />
                ))}
                {rec.candidate_items.length === 0 && (
                  <p className="text-sm text-content-faint">
                    Aucun article disponible pour ce matériel.
                  </p>
                )}
              </div>
            </div>
          ))}
        </CardBody>
      </Card>

      <Card>
        <CardHeader
          title="Ajouter d'autres articles"
          description="Recherchez n'importe quel article de l'inventaire, même hors des catalogues demandés."
        />
        <CardBody className="flex flex-col gap-3">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-content-faint" />
            <input
              value={itemSearch}
              onChange={(e) => setItemSearch(e.target.value)}
              placeholder="Rechercher un article ou une référence…"
              className="h-10 w-full rounded-lg border border-border bg-surface pl-9 pr-3 text-sm text-content placeholder:text-content-faint outline-none transition-colors focus:border-primary/70 focus:ring-2 focus:ring-primary/25"
            />
          </div>

          {itemSearch.trim() && (
            <div className="grid gap-2 sm:grid-cols-2">
              {extraMatches.length === 0 ? (
                <p className="text-sm text-content-faint">Aucun article trouvé.</p>
              ) : (
                extraMatches.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => toggle(item.id)}
                    className={cn(
                      "flex items-center gap-3 rounded-lg border p-2.5 text-left transition-colors",
                      selected.has(item.id)
                        ? "border-primary/50 bg-danger-bg"
                        : "border-border hover:border-border-strong hover:bg-surface-raised",
                    )}
                  >
                    <div
                      className={cn(
                        "flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors",
                        selected.has(item.id)
                          ? "border-primary bg-primary text-white"
                          : "border-border-strong",
                      )}
                    >
                      {selected.has(item.id) && <Check className="size-3.5" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{item.name}</p>
                      <p className="truncate text-[11px] text-content-faint">
                        {item.catalog.name}
                      </p>
                    </div>
                  </button>
                ))
              )}
            </div>
          )}

          {extraSelected.length > 0 && (
            <div className="flex flex-wrap gap-1.5 border-t border-border pt-3">
              {extraSelected.map((id) => (
                <span
                  key={id}
                  className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-danger-bg px-2.5 py-1 text-xs text-brand-200"
                >
                  {itemById.get(id)?.name ?? `#${id}`}
                  <button
                    onClick={() => toggle(id)}
                    className="text-brand-300/70 hover:text-brand-200"
                    aria-label="Retirer"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          )}
        </CardBody>
      </Card>
      </div>

      <div className="flex flex-col gap-6">
        <Card>
          <CardHeader title="Informations" />
          <CardBody className="flex flex-col gap-3 text-sm">
            <InfoRow icon={UserIcon} label="Demandeur">
              <div className="flex items-center gap-2">
                <Avatar name={request.borrower.name} size="sm" />
                {request.borrower.name}
              </div>
            </InfoRow>
            <InfoRow icon={Phone} label="Téléphone">
              {request.phone_number}
            </InfoRow>
            <InfoRow icon={CalendarRange} label="Période souhaitée">
              {formatDateShort(request.start_date)} →{" "}
              {formatDateShort(request.end_date)}
            </InfoRow>
            {request.reason && (
              <div className="rounded-lg bg-surface-raised p-3 text-content-muted">
                {request.reason}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader
            title="Créer le prêt"
            description={`${selected.size} article(s) sélectionné(s)`}
          />
          <CardBody className="flex flex-col gap-4">
            <DateRangeField
              start={start}
              end={end}
              onStartChange={setStart}
              onEndChange={setEnd}
              required
              stack
            />
            <Field
              label="Caution (€)"
              hint="Suggérée d'après les articles sélectionnés"
            >
              <Input
                type="number"
                min="0"
                step="0.01"
                value={depositValue}
                onChange={(e) => setDepositOverride(e.target.value)}
              />
            </Field>
            <Field label="Commentaire" htmlFor="comments">
              <Textarea
                id="comments"
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="Note interne (optionnel)"
              />
            </Field>
            {error && (
              <p className="rounded-lg border border-danger/30 bg-danger-bg px-3 py-2 text-sm text-brand-300">
                {error}
              </p>
            )}
            <Button
              onClick={submit}
              loading={create.isPending}
              disabled={selected.size === 0}
            >
              Créer le prêt
            </Button>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}

function CandidateItem({
  item,
  deposit,
  selected,
  onToggle,
}: {
  item: RequestRecommendationItem;
  deposit?: number;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={cn(
        "flex items-center gap-3 rounded-lg border p-2.5 text-left transition-colors",
        selected
          ? "border-primary/50 bg-danger-bg"
          : "border-border hover:border-border-strong hover:bg-surface-raised",
      )}
    >
      <div
        className={cn(
          "flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors",
          selected
            ? "border-primary bg-primary text-white"
            : "border-border-strong",
        )}
      >
        {selected && <Check className="size-3.5" />}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{item.item_name}</p>
        <div className="mt-0.5 flex items-center gap-2">
          {item.has_date_conflict && (
            <span className="inline-flex items-center gap-1 text-[11px] text-warning">
              <TriangleAlert className="size-3" /> Conflit de dates
            </span>
          )}
          {deposit !== undefined && deposit > 0 && (
            <span className="text-[11px] text-content-faint">
              {formatMoney(deposit)}
            </span>
          )}
        </div>
      </div>
      {item.availability !== "available" && (
        <Badge tone="warning">{item.availability}</Badge>
      )}
    </button>
  );
}

function InfoRow({
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
