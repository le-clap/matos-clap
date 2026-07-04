import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { DateRangeField } from "@/components/ui/DateRangeField";
import { Field } from "@/components/ui/Field";
import { Input, Select, Textarea } from "@/components/ui/Input";
import { PageSpinner } from "@/components/ui/Spinner";
import { useToast } from "@/components/ui/Toast";
import { ItemMultiSelect } from "@/features/loans/ItemMultiSelect";
import { useItems } from "@/hooks/useInventory";
import { useLoanMutations } from "@/hooks/useLoans";
import { useUsers } from "@/hooks/useUsers";
import { ApiError } from "@/lib/api";
import { localInputToIso } from "@/lib/format";

export function AdminNewLoanPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const { data: users, isLoading: usersLoading } = useUsers();
  const { data: items } = useItems();
  const { create } = useLoanMutations();

  const [borrowerId, setBorrowerId] = useState<number | "">("");
  const [itemIds, setItemIds] = useState<number[]>([]);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [depositOverride, setDepositOverride] = useState<string | null>(null);
  const [comments, setComments] = useState("");
  const [error, setError] = useState<string | null>(null);

  const depositByItem = useMemo(() => {
    const map = new Map<number, number>();
    items?.forEach((i) => map.set(i.id, i.deposit_cents));
    return map;
  }, [items]);

  const suggestedDeposit = useMemo(
    () => itemIds.reduce((sum, id) => sum + (depositByItem.get(id) ?? 0), 0),
    [itemIds, depositByItem],
  );
  const depositValue = depositOverride ?? (suggestedDeposit / 100).toFixed(2);

  const datesValid = !!start && !!end && new Date(start) < new Date(end);

  const submit = async () => {
    setError(null);
    if (!borrowerId) return setError("Sélectionnez un emprunteur.");
    if (itemIds.length === 0) return setError("Sélectionnez au moins un article.");
    if (!datesValid) return setError("Période invalide.");
    try {
      const res = await create.mutateAsync({
        borrower_id: Number(borrowerId),
        start_date: localInputToIso(start),
        end_date: localInputToIso(end),
        item_ids: itemIds,
        total_deposit_cents: Math.round(parseFloat(depositValue || "0") * 100),
        comments: comments.trim() || null,
      });
      if (res.warnings.length > 0) {
        toast.toast({
          tone: "warning",
          title: "Prêt créé avec avertissements",
          description: res.warnings.map((w) => w.message).join(" · "),
        });
      } else {
        toast.success("Prêt créé");
      }
      navigate(`/admin/loans/${res.loan.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail ?? err.message : "Erreur");
    }
  };

  if (usersLoading) return <PageSpinner />;

  return (
    <div>
      <PageHeader
        title="Nouveau prêt"
        description="Créez un prêt directement, sans demande préalable."
        back={{ to: "/admin/loans", label: "Prêts" }}
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader title="Matériel" description="Recherchez et ajoutez les articles à prêter." />
          <CardBody>
            <ItemMultiSelect
              items={items ?? []}
              selected={itemIds}
              onChange={setItemIds}
            />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Détails du prêt" />
          <CardBody className="flex flex-col gap-4">
            <Field label="Emprunteur" required>
              <Select
                value={borrowerId}
                onChange={(e) =>
                  setBorrowerId(e.target.value ? Number(e.target.value) : "")
                }
              >
                <option value="">— Choisir —</option>
                {users?.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.username})
                  </option>
                ))}
              </Select>
            </Field>
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
            <Field label="Commentaire">
              <Textarea
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
            <Button onClick={submit} loading={create.isPending}>
              Créer le prêt
            </Button>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
