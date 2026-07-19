import { PackageCheck, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/auth/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Pagination } from "@/components/ui/Pagination";
import { Skeleton } from "@/components/ui/Skeleton";
import { LoanStatusBadge } from "@/components/ui/StatusBadge";
import { useLoans } from "@/hooks/useLoans";
import { formatDateShort, formatMoney } from "@/lib/format";
import { isOverdue } from "@/lib/loanStatus";

const LIMIT = 10;

export function MyLoansPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(0);
  const { data, isLoading } = useLoans({
    borrowerId: user?.id,
    page,
    limit: LIMIT,
  });

  return (
    <div>
      <PageHeader
        title="Mes prêts"
        description="Le matériel qui vous est confié et son historique."
      />

      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-card" />
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={PackageCheck}
          title="Aucun prêt"
          description="Vous n'avez aucun prêt en cours ni passé pour le moment."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {data.items.map((loan) => {
            const status = loan.status;
            const overdue = isOverdue(loan);
            return (
              <Card key={loan.id}>
                <CardBody className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <LoanStatusBadge status={status} />
                      {overdue && (
                        <Badge tone="danger" dot>
                          <TriangleAlert className="size-3" /> En retard
                        </Badge>
                      )}
                      <span className="text-xs text-content-faint">
                        Prêt #{loan.id}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-content">
                      Du <strong>{formatDateShort(loan.start_date)}</strong> au{" "}
                      <strong>{formatDateShort(loan.end_date)}</strong>
                    </p>
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {loan.loaned_items.map((li) => (
                        <Badge
                          key={li.id}
                          tone={li.actual_return_date ? "neutral" : "info"}
                        >
                          {li.item.name}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  {loan.total_deposit_cents > 0 && (
                    <div className="text-right">
                      <p className="text-xs text-content-faint">Caution</p>
                      <p className="font-semibold tabular-nums">
                        {formatMoney(loan.total_deposit_cents)}
                      </p>
                    </div>
                  )}
                </CardBody>
              </Card>
            );
          })}
          <Pagination
            page={page}
            limit={LIMIT}
            total={data.total}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  );
}
