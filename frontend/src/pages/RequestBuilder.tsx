import { PackageOpen, SendHorizonal, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/auth/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { DateRangeField } from '@/components/ui/DateRangeField';
import { EmptyState } from '@/components/ui/EmptyState';
import { Field } from '@/components/ui/Field';
import { Input, Textarea } from '@/components/ui/Input';
import { QuantityStepper } from '@/components/ui/QuantityStepper';
import { useToast } from '@/components/ui/Toast';
import { CatalogThumb } from '@/features/catalog/CatalogCard';
import { useCart } from '@/features/cart/CartContext';
import { useRequestMutations } from '@/hooks/useRequests';
import { ApiError } from '@/lib/api';
import { daysBetween, localInputToIso } from '@/lib/format';
import { PHONE_HINT, isValidPhone } from '@/lib/validation';

export function RequestBuilderPage() {
  const { user } = useAuth();
  const { lines, setQuantity, remove, clear, count } = useCart();
  const { create } = useRequestMutations();
  const toast = useToast();
  const navigate = useNavigate();

  const [phone, setPhone] = useState('');
  const [reason, setReason] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [error, setError] = useState<string | null>(null);

  const datesValid = !!start && !!end && new Date(start) < new Date(end);

  const submit = async () => {
    setError(null);
    if (!user) return;
    if (lines.length === 0) return setError('Votre demande est vide.');
    if (!phone.trim()) return setError('Veuillez indiquer un numéro de téléphone.');
    if (!isValidPhone(phone)) return setError('Numéro de téléphone invalide (ex. 06 12 34 56 78).');
    if (!datesValid) return setError('La date de fin doit être postérieure à la date de début.');

    try {
      await create.mutateAsync({
        borrower_id: user.id,
        phone_number: phone.trim(),
        start_date: localInputToIso(start),
        end_date: localInputToIso(end),
        reason: reason.trim() || null,
        requested_catalogs: lines.map((l) => ({
          catalog_id: l.catalogId,
          quantity: l.quantity,
        })),
      });
      clear();
      toast.success('Demande envoyée', "Le CLAP va l'étudier et revenir vers vous.");
      navigate('/my/requests');
    } catch (err) {
      setError(err instanceof ApiError ? (err.detail ?? err.message) : 'Erreur inconnue');
    }
  };

  if (count === 0) {
    return (
      <div>
        <PageHeader title="Ma demande de prêt" />
        <EmptyState
          icon={PackageOpen}
          title="Votre demande est vide"
          description="Ajoutez du matériel depuis le catalogue pour constituer votre demande."
          action={
            <Button asChild>
              <Link to="/catalog">Parcourir le catalogue</Link>
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Ma demande de prêt"
        description="Vérifiez le matériel et précisez la période souhaitée."
      />

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        {/* Cart lines */}
        <Card>
          <div className="divide-y divide-border">
            {lines.map((line) => (
              <div key={line.catalogId} className="flex items-center gap-3 p-3.5">
                <div className="size-14 shrink-0 overflow-hidden rounded-lg border border-border">
                  <CatalogThumb imagePath={line.imagePath} />
                </div>
                <div className="min-w-0 flex-1">
                  <Link
                    to={`/catalog/${line.catalogId}`}
                    className="truncate font-medium text-content hover:text-primary"
                  >
                    {line.name}
                  </Link>
                </div>
                <QuantityStepper
                  value={line.quantity}
                  onChange={(q) => setQuantity(line.catalogId, q)}
                />
                <button
                  onClick={() => remove(line.catalogId)}
                  className="rounded-lg p-2 text-content-faint transition-colors hover:bg-danger-bg hover:text-brand-300"
                  aria-label="Retirer"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            ))}
          </div>
        </Card>

        {/* Details + submit */}
        <Card>
          <CardBody className="flex flex-col gap-4">
            <DateRangeField
              start={start}
              end={end}
              onStartChange={setStart}
              onEndChange={setEnd}
              required
              stack
            />
            {datesValid && (
              <p className="-mt-1 text-xs text-content-faint">
                Durée : {daysBetween(start, end)} jour(s)
              </p>
            )}
            <Field
              label="Téléphone"
              required
              htmlFor="phone"
              hint={PHONE_HINT}
              error={phone && !isValidPhone(phone) ? 'Numéro invalide' : null}
            >
              <Input
                id="phone"
                type="tel"
                placeholder="06 12 34 56 78"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </Field>
            <Field label="Motif" hint="Tournage, projet, événement… (optionnel)" htmlFor="reason">
              <Textarea
                id="reason"
                placeholder="Décrivez brièvement votre projet"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </Field>

            {error && (
              <p className="rounded-lg border border-danger/30 bg-danger-bg px-3 py-2 text-sm text-brand-300">
                {error}
              </p>
            )}

            <Button onClick={submit} loading={create.isPending} size="lg">
              <SendHorizonal className="size-4" />
              Envoyer la demande
            </Button>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
