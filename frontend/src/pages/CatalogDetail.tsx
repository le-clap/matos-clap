import { CalendarCheck, Plus, ShoppingBag } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { DateRangeField } from "@/components/ui/DateRangeField";
import { EmptyState } from "@/components/ui/EmptyState";
import { QuantityStepper } from "@/components/ui/QuantityStepper";
import { PageSpinner } from "@/components/ui/Spinner";
import { CatalogThumb } from "@/features/catalog/CatalogCard";
import { useCart } from "@/features/cart/CartContext";
import { useCatalog, useCatalogAvailability } from "@/hooks/useInventory";
import { localInputToIso } from "@/lib/format";
import { cn } from "@/lib/utils";

export function CatalogDetailPage() {
  const { id } = useParams();
  const catalogId = Number(id);
  const { add } = useCart();
  const [quantity, setQuantity] = useState(1);

  const { data: catalog, isLoading } = useCatalog(catalogId);

  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const rangeReady = !!start && !!end && new Date(start) < new Date(end);
  const startIso = rangeReady ? localInputToIso(start) : "";
  const endIso = rangeReady ? localInputToIso(end) : "";
  const { data: availability, isFetching } = useCatalogAvailability(
    catalogId,
    startIso,
    endIso,
    rangeReady,
  );

  const availableCount = availability?.available.length ?? 0;
  const totalCount =
    (availability?.available.length ?? 0) + (availability?.unavailable.length ?? 0);

  if (isLoading) return <PageSpinner />;
  if (!catalog) {
    return (
      <EmptyState title="Matériel introuvable" description="Ce matériel n'existe pas." />
    );
  }

  return (
    <div>
      <PageHeader
        title={catalog.name}
        description={catalog.category.name}
        back={{ to: "/catalog", label: "Catalogue" }}
      />

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <Card className="overflow-hidden">
          <div className="aspect-[16/9] w-full">
            <CatalogThumb imagePath={catalog.image_path} />
          </div>
          {catalog.description && (
            <CardBody>
              <p className="text-sm leading-relaxed text-content-muted">
                {catalog.description}
              </p>
            </CardBody>
          )}
        </Card>

        <div className="flex flex-col gap-6">
          <Card>
            <CardBody>
              <h3 className="font-semibold">Ajouter à ma demande</h3>
              <p className="mt-1 text-sm text-content-muted">
                Choisissez la quantité souhaitée.
              </p>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-sm text-content-muted">Quantité</span>
                <QuantityStepper value={quantity} onChange={setQuantity} />
              </div>
              <Button
                className="mt-4 w-full"
                onClick={() =>
                  add(
                    {
                      catalogId: catalog.id,
                      name: catalog.name,
                      imagePath: catalog.image_path,
                    },
                    quantity,
                  )
                }
              >
                <Plus className="size-4" />
                Ajouter à la demande
              </Button>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <h3 className="flex items-center gap-2 font-semibold">
                <CalendarCheck className="size-4 text-primary" />
                Disponibilité
              </h3>
              <p className="mt-1 text-sm text-content-muted">
                Vérifiez combien d'articles sont libres sur une période.
              </p>
              <div className="mt-4">
                <DateRangeField
                  start={start}
                  end={end}
                  onStartChange={setStart}
                  onEndChange={setEnd}
                  stack
                />
              </div>

              {rangeReady && (
                <div
                  className={cn(
                    "mt-4 rounded-lg border p-4 text-center",
                    isFetching
                      ? "border-border bg-surface-raised"
                      : availableCount > 0
                        ? "border-success/30 bg-success-bg"
                        : "border-warning/30 bg-warning-bg",
                  )}
                >
                  {isFetching ? (
                    <p className="text-sm text-content-muted">Vérification…</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold tabular-nums">
                        {availableCount}
                        <span className="text-base font-normal text-content-muted">
                          {" "}
                          / {totalCount}
                        </span>
                      </p>
                      <p className="mt-0.5 text-xs text-content-muted">
                        article(s) disponible(s) sur cette période
                      </p>
                    </>
                  )}
                </div>
              )}
            </CardBody>
          </Card>

          <Button asChild variant="secondary" className="w-full">
            <Link to="/request">
              <ShoppingBag className="size-4" />
              Voir ma demande
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
