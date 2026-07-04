import {
  ArrowRight,
  ClipboardList,
  Package,
  PackageCheck,
  ScrollText,
  TriangleAlert,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { LoanStatusBadge, RequestStatusBadge } from "@/components/ui/StatusBadge";
import { Table, TBody, Td, Th, THead, Tr } from "@/components/ui/Table";
import { useCatalogs, useItems } from "@/hooks/useInventory";
import { useLoans } from "@/hooks/useLoans";
import { useRequests } from "@/hooks/useRequests";
import { formatDateShort } from "@/lib/format";
import { isOverdue } from "@/lib/loanStatus";
import { cn } from "@/lib/utils";

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const pending = useRequests({ processed: false, limit: 5 });
  const activeLoans = useLoans({ active: true, limit: 100 });
  const recentLoans = useLoans({ limit: 5 });
  const catalogs = useCatalogs();
  const items = useItems();

  const maintenanceCount =
    items.data?.filter((i) => i.availability === "maintenance").length ?? 0;
  const overdueCount =
    activeLoans.data?.items.filter(isOverdue).length ?? 0;

  // Flatten active loans into the individual articles currently out.
  const outItems = (activeLoans.data?.items ?? []).flatMap((loan) =>
    loan.loaned_items
      .filter((li) => !li.actual_return_date)
      .map((li) => ({
        key: li.id,
        itemName: li.item.name,
        borrowerName: loan.borrower.name,
        loanId: loan.id,
        endDate: loan.end_date,
        overdue: isOverdue(loan),
      })),
  );

  return (
    <div>
      <PageHeader
        title={`Bonjour, ${user?.name.split(" ")[0] ?? ""}`}
        description="Vue d'ensemble de l'activité du parc matériel."
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          icon={ClipboardList}
          label="Demandes en attente"
          value={pending.data?.total}
          loading={pending.isLoading}
          to="/admin/requests"
          tone="warning"
        />
        <StatCard
          icon={ScrollText}
          label="Prêts en cours"
          value={activeLoans.data?.total}
          loading={activeLoans.isLoading}
          to="/admin/loans"
          tone="success"
        />
        <StatCard
          icon={Package}
          label="Références"
          value={catalogs.data?.length}
          loading={catalogs.isLoading}
          to="/admin/inventory"
        />
        <StatCard
          icon={Wrench}
          label="En maintenance"
          value={maintenanceCount}
          loading={items.isLoading}
          tone={maintenanceCount > 0 ? "warning" : "neutral"}
        />
      </div>

      {overdueCount > 0 && (
        <div className="mt-4 flex items-center gap-3 rounded-[var(--radius-card)] border border-danger/30 bg-danger-bg px-4 py-3 text-sm">
          <TriangleAlert className="size-5 shrink-0 text-brand-400" />
          <span className="text-brand-200">
            <strong>{overdueCount}</strong> prêt(s) en cours ont dépassé leur date
            de retour prévue.
          </span>
          <Link
            to="/admin/loans"
            className="ml-auto shrink-0 font-medium text-brand-300 hover:underline"
          >
            Voir
          </Link>
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <ListHeader
            title="Demandes à traiter"
            to="/admin/requests"
            icon={ClipboardList}
          />
          <CardBody className="flex flex-col gap-1 p-2">
            {pending.isLoading ? (
              <SkeletonRows />
            ) : pending.data && pending.data.items.length > 0 ? (
              pending.data.items.map((req) => (
                <Link
                  key={req.id}
                  to={`/admin/requests/${req.id}`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors hover:bg-surface-raised"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {req.borrower.name}
                    </p>
                    <p className="truncate text-xs text-content-faint">
                      {req.requested_catalogs.length} référence(s) ·{" "}
                      {formatDateShort(req.start_date)}
                    </p>
                  </div>
                  <RequestStatusBadge refused={req.refused} loanId={req.loan_id} />
                  <ArrowRight className="size-4 text-content-faint" />
                </Link>
              ))
            ) : (
              <Empty label="Aucune demande en attente" />
            )}
          </CardBody>
        </Card>

        <Card>
          <ListHeader title="Prêts récents" to="/admin/loans" icon={ScrollText} />
          <CardBody className="flex flex-col gap-1 p-2">
            {recentLoans.isLoading ? (
              <SkeletonRows />
            ) : recentLoans.data && recentLoans.data.items.length > 0 ? (
              recentLoans.data.items.map((loan) => (
                <Link
                  key={loan.id}
                  to={`/admin/loans/${loan.id}`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors hover:bg-surface-raised"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {loan.borrower.name}
                    </p>
                    <p className="truncate text-xs text-content-faint">
                      {loan.loaned_items.length} article(s) ·{" "}
                      {formatDateShort(loan.start_date)}
                    </p>
                  </div>
                  {isOverdue(loan) ? (
                    <Badge tone="danger" dot>
                      Retard
                    </Badge>
                  ) : (
                    <LoanStatusBadge status={loan.status} />
                  )}
                  <ArrowRight className="size-4 text-content-faint" />
                </Link>
              ))
            ) : (
              <Empty label="Aucun prêt enregistré" />
            )}
          </CardBody>
        </Card>
      </div>

      <div className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <PackageCheck className="size-5 text-content-faint" />
            Matériel actuellement sorti
          </h2>
          {!activeLoans.isLoading && (
            <span className="text-sm text-content-muted">
              {outItems.length} article{outItems.length > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {activeLoans.isLoading ? (
          <Skeleton className="h-40 rounded-[var(--radius-card)]" />
        ) : outItems.length === 0 ? (
          <EmptyState
            icon={PackageCheck}
            title="Rien dehors"
            description="Aucun matériel n'est actuellement prêté."
          />
        ) : (
          <Table>
            <THead>
              <Tr>
                <Th>Article</Th>
                <Th>Emprunteur</Th>
                <Th>Retour prévu</Th>
              </Tr>
            </THead>
            <TBody>
              {outItems.map((o) => (
                <Tr
                  key={o.key}
                  className="cursor-pointer"
                  onClick={() => navigate(`/admin/loans/${o.loanId}`)}
                >
                  <Td className="font-medium">{o.itemName}</Td>
                  <Td>
                    <div className="flex items-center gap-2.5">
                      <Avatar name={o.borrowerName} size="sm" />
                      {o.borrowerName}
                    </div>
                  </Td>
                  <Td>
                    <div className="flex items-center gap-2">
                      <span className="text-content-muted">
                        {formatDateShort(o.endDate)}
                      </span>
                      {o.overdue && (
                        <Badge tone="danger" dot>
                          En retard
                        </Badge>
                      )}
                    </div>
                  </Td>
                </Tr>
              ))}
            </TBody>
          </Table>
        )}
      </div>
    </div>
  );
}

const toneStyles = {
  neutral: "text-content-muted",
  success: "text-success",
  warning: "text-warning",
};

function StatCard({
  icon: Icon,
  label,
  value,
  loading,
  to,
  tone = "neutral",
}: {
  icon: LucideIcon;
  label: string;
  value?: number;
  loading?: boolean;
  to?: string;
  tone?: keyof typeof toneStyles;
}) {
  const content = (
    <Card className={cn("transition-colors", to && "hover:border-border-strong")}>
      <CardBody className="flex items-center gap-4">
        <div
          className={cn(
            "flex size-11 shrink-0 items-center justify-center rounded-xl bg-surface-raised",
            toneStyles[tone],
          )}
        >
          <Icon className="size-5" />
        </div>
        <div className="min-w-0">
          {loading ? (
            <Skeleton className="h-7 w-12" />
          ) : (
            <p className="text-2xl font-bold tabular-nums leading-none">
              {value ?? 0}
            </p>
          )}
          <p className="mt-1.5 truncate text-[13px] text-content-muted">{label}</p>
        </div>
      </CardBody>
    </Card>
  );
  return to ? <Link to={to}>{content}</Link> : content;
}

function ListHeader({
  title,
  to,
  icon: Icon,
}: {
  title: string;
  to: string;
  icon: LucideIcon;
}) {
  return (
    <div className="flex items-center justify-between border-b border-border px-4 py-3.5">
      <h3 className="flex items-center gap-2 font-semibold">
        <Icon className="size-4 text-content-faint" />
        {title}
      </h3>
      <Link
        to={to}
        className="text-sm text-content-muted transition-colors hover:text-content"
      >
        Tout voir
      </Link>
    </div>
  );
}

function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} className="h-12 rounded-lg" />
      ))}
    </>
  );
}

function Empty({ label }: { label: string }) {
  return (
    <p className="px-3 py-8 text-center text-sm text-content-faint">{label}</p>
  );
}
