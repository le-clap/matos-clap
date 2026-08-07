import { ClipboardList } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/PageHeader';
import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Pagination } from '@/components/ui/Pagination';
import { SearchInput } from '@/components/ui/SearchInput';
import { Skeleton } from '@/components/ui/Skeleton';
import { RequestStatusBadge } from '@/components/ui/StatusBadge';
import { Table, TBody, Td, Th, THead, Tr } from '@/components/ui/Table';
import { Tabs } from '@/components/ui/Tabs';
import { useRequests } from '@/hooks/useRequests';
import { formatDateShort } from '@/lib/format';
import { useDebounce } from '@/hooks/useDebounce.ts';

const LIMIT = 15;
type Filter = 'all' | 'pending' | 'processed';

export function AdminRequestsPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<Filter>('pending');
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search);

  const processed = filter === 'pending' ? false : filter === 'processed' ? true : undefined;
  const { data, isLoading } = useRequests({
    processed,
    page,
    limit: LIMIT,
    search: debouncedSearch,
  });

  const rows = data?.items ?? [];

  return (
    <div>
      <PageHeader
        title="Demandes"
        description="Étudiez les demandes de prêt et transformez-les en prêts."
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Tabs
          value={filter}
          onChange={(v) => {
            setFilter(v);
            setPage(0);
          }}
          items={[
            { value: 'pending', label: 'En attente' },
            { value: 'processed', label: 'Traitées' },
            { value: 'all', label: 'Toutes' },
          ]}
        />
        <SearchInput
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(0);
          }}
          placeholder="Rechercher un demandeur…"
          className="sm:w-64"
        />
      </div>

      {isLoading ? (
        <Skeleton className="h-64 rounded-[var(--radius-card)]" />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={ClipboardList}
          title="Aucune demande"
          description="Aucune demande ne correspond à ce filtre."
        />
      ) : (
        <div className="flex flex-col gap-4">
          <Table>
            <THead>
              <Tr>
                <Th>Demandeur</Th>
                <Th>Période</Th>
                <Th>Matériel</Th>
                <Th>Statut</Th>
              </Tr>
            </THead>
            <TBody>
              {rows.map((req) => (
                <Tr
                  key={req.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/admin/requests/${req.id}`)}
                >
                  <Td>
                    <div className="flex items-center gap-2.5">
                      <Avatar name={req.borrower.name} size="sm" />
                      <div>
                        <p className="font-medium">{req.borrower.name}</p>
                        <p className="text-xs text-content-faint">
                          #{req.id} · {formatDateShort(req.created_at)}
                        </p>
                      </div>
                    </div>
                  </Td>
                  <Td className="whitespace-nowrap text-content-muted">
                    {formatDateShort(req.start_date)} → {formatDateShort(req.end_date)}
                  </Td>
                  <Td>
                    <div className="flex flex-wrap gap-1">
                      {req.requested_catalogs.slice(0, 3).map((rc) => (
                        <Badge key={rc.id} tone="neutral">
                          {rc.quantity}× {rc.catalog.name}
                        </Badge>
                      ))}
                      {req.requested_catalogs.length > 3 && (
                        <Badge tone="neutral">+{req.requested_catalogs.length - 3}</Badge>
                      )}
                    </div>
                  </Td>
                  <Td>
                    <RequestStatusBadge refused={req.refused} loanId={req.loan_id} />
                  </Td>
                </Tr>
              ))}
            </TBody>
          </Table>
          <Pagination page={page} limit={LIMIT} total={data?.total ?? 0} onPageChange={setPage} />
        </div>
      )}
    </div>
  );
}
