import {Plus, ScrollText, TriangleAlert} from "lucide-react";
import {useState} from "react";
import {Link, useNavigate} from "react-router-dom";
import {PageHeader} from "@/components/PageHeader";
import {Avatar} from "@/components/ui/Avatar";
import {Badge} from "@/components/ui/Badge";
import {Button} from "@/components/ui/Button";
import {EmptyState} from "@/components/ui/EmptyState";
import {Pagination} from "@/components/ui/Pagination";
import {SearchInput} from "@/components/ui/SearchInput";
import {Skeleton} from "@/components/ui/Skeleton";
import {LoanStatusBadge} from "@/components/ui/StatusBadge";
import {Table, TBody, Td, Th, THead, Tr} from "@/components/ui/Table";
import {Tabs} from "@/components/ui/Tabs";
import {useLoans} from "@/hooks/useLoans";
import {formatDateShort, formatMoney} from "@/lib/format";
import {isOverdue} from "@/lib/loanStatus";
import {useDebounce} from "@/hooks/useDebounce.ts";

const LIMIT = 15;
type Filter = "scheduled" | "active" | "returned" | "all";

export function AdminLoansPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<Filter>("active");
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("")
  const debouncedSearch = useDebounce(search);

  const status = filter === "all" ? undefined : filter;
  const { data, isLoading } = useLoans({ status, page, limit: LIMIT, search:debouncedSearch });

  const rows = data?.items ?? [];

  return (
    <div>
      <PageHeader
        title="Prêts"
        description="Gérez les prêts en cours, planifiés et rendus."
        action={
          <Button asChild>
            <Link to="/admin/loans/new">
              <Plus className="size-4"/> Nouveau prêt
            </Link>
          </Button>
        }
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Tabs
          value={filter}
          onChange={(v) => {
            setFilter(v);
            setPage(0);
          }}
          items={[
            { value: "active", label: "En cours" },
            { value: "scheduled", label: "Planifiés" },
            { value: "returned", label: "Rendus" },
            { value: "all", label: "Tous" },
          ]}
        />
        <SearchInput
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(0);
          }}
          placeholder="Rechercher un emprunteur…"
          className="sm:w-64"
        />
      </div>

      {isLoading ? (
        <Skeleton className="h-64 rounded-[var(--radius-card)]"/>
      ) : rows.length === 0 ? (
        <EmptyState
          icon={ScrollText}
          title="Aucun prêt"
          description="Aucun prêt ne correspond à ce filtre."
        />
      ) : (
        <div className="flex flex-col gap-4">
          <Table>
            <THead>
              <Tr>
                <Th>Emprunteur</Th>
                <Th>Période</Th>
                <Th>Articles</Th>
                <Th>Caution</Th>
                <Th>Statut</Th>
              </Tr>
            </THead>
            <TBody>
              {rows.map((loan) => (
                <Tr
                  key={loan.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/admin/loans/${loan.id}`)}
                >
                  <Td>
                    <div className="flex items-center gap-2.5">
                      <Avatar name={loan.borrower.name} size="sm"/>
                      <div>
                        <p className="font-medium">{loan.borrower.name}</p>
                        <p className="text-xs text-content-faint">#{loan.id}</p>
                      </div>
                    </div>
                  </Td>
                  <Td className="whitespace-nowrap text-content-muted">
                    {formatDateShort(loan.start_date)} →{" "}
                    {formatDateShort(loan.end_date)}
                  </Td>
                  <Td className="text-content-muted tabular-nums">
                    {loan.loaned_items.length}
                  </Td>
                  <Td className="tabular-nums">
                    {loan.total_deposit_cents > 0
                      ? formatMoney(loan.total_deposit_cents)
                      : "—"}
                  </Td>
                  <Td>
                    <div className="flex items-center gap-1.5">
                      <LoanStatusBadge status={loan.status}/>
                      {isOverdue(loan) && (
                        <Badge tone="danger" dot>
                          <TriangleAlert className="size-3"/> Retard
                        </Badge>
                      )}
                    </div>
                  </Td>
                </Tr>
              ))}
            </TBody>
          </Table>
          <Pagination
            page={page}
            limit={LIMIT}
            total={data?.total ?? 0}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  );
}
