import { ShieldCheck, Users as UsersIcon } from 'lucide-react';
import { useState } from 'react';
import type { AccessLevel, UserPublic } from '@/client';
import { useAuth } from '@/auth/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { Field } from '@/components/ui/Field';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { SearchInput } from '@/components/ui/SearchInput';
import { Select } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import { Table, TBody, Td, Th, THead, Tr } from '@/components/ui/Table';
import { Tabs } from '@/components/ui/Tabs';
import { useToast } from '@/components/ui/Toast';
import { useDebounce } from '@/hooks/useDebounce';
import { useUserMutations, useUsers } from '@/hooks/useUsers';
import { ROLE_LABELS, ROLE_ORDER } from '@/lib/roles';

const LIMIT = 15;

type RoleFilter = AccessLevel | 'all';

const roleTone: Record<AccessLevel, Parameters<typeof Badge>[0]['tone']> = {
  user: 'neutral',
  clap: 'info',
  manager: 'warning',
  admin: 'brand',
};

export function AdminUsersPage() {
  const { hasRole } = useAuth();
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('all');
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search);
  const [editing, setEditing] = useState<UserPublic | null>(null);

  const canEdit = hasRole('admin');

  const { data, isLoading } = useUsers({
    accessLevel: roleFilter === 'all' ? undefined : roleFilter,
    page,
    limit: LIMIT,
    search: debouncedSearch,
  });

  const rows = data?.items ?? [];

  return (
    <div>
      <PageHeader
        title="Utilisateurs"
        description={
          canEdit
            ? 'Consultez les membres et gérez leurs rôles.'
            : 'Consultez les membres de la plateforme.'
        }
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Tabs
          value={roleFilter}
          onChange={(v) => {
            setRoleFilter(v);
            setPage(0);
          }}
          items={[
            { value: 'all', label: 'Tous' },
            ...ROLE_ORDER.map((r) => ({ value: r, label: ROLE_LABELS[r] })),
          ]}
        />
        <SearchInput
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(0);
          }}
          placeholder="Rechercher un membre…"
          className="sm:w-64"
        />
      </div>

      {isLoading ? (
        <Skeleton className="h-64 rounded-card" />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={UsersIcon}
          title="Aucun utilisateur"
          description="Aucun membre ne correspond à cette recherche."
        />
      ) : (
        <div className="flex flex-col gap-4">
          <Table>
            <THead>
              <Tr>
                <Th>Membre</Th>
                <Th>Identifiant</Th>
                <Th>Email</Th>
                <Th>Rôle</Th>
                {canEdit && <Th className="w-px" />}
              </Tr>
            </THead>
            <TBody>
              {rows.map((u) => (
                <Tr key={u.id}>
                  <Td>
                    <div className="flex items-center gap-2.5">
                      <Avatar name={u.name} size="sm" />
                      <span className="font-medium">{u.name}</span>
                    </div>
                  </Td>
                  <Td className="text-content-muted">{u.username}</Td>
                  <Td className="text-content-muted">{u.email}</Td>
                  <Td>
                    <Badge tone={roleTone[u.access_level]}>{ROLE_LABELS[u.access_level]}</Badge>
                  </Td>
                  {canEdit && (
                    <Td>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditing(u)}
                        className="gap-1.5"
                      >
                        <ShieldCheck className="size-4" />
                        Rôle
                      </Button>
                    </Td>
                  )}
                </Tr>
              ))}
            </TBody>
          </Table>
          <Pagination page={page} limit={LIMIT} total={data?.total ?? 0} onPageChange={setPage} />
        </div>
      )}

      {editing && <RoleModal user={editing} onClose={() => setEditing(null)} />}
    </div>
  );
}

function RoleModal({ user, onClose }: { user: UserPublic; onClose: () => void }) {
  const { updateRole } = useUserMutations();
  const toast = useToast();
  const [role, setRole] = useState<AccessLevel>(user.access_level);

  return (
    <Modal
      open
      onClose={onClose}
      title="Modifier le rôle"
      description={user.name}
      size="sm"
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={updateRole.isPending}
            disabled={role === user.access_level}
            onClick={async () => {
              await updateRole.mutateAsync({
                id: user.id,
                body: { access_level: role },
              });
              toast.success('Rôle mis à jour');
              onClose();
            }}
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <Field label="Niveau d'accès">
        <Select value={role} onChange={(e) => setRole(e.target.value as AccessLevel)}>
          {ROLE_ORDER.map((r) => (
            <option key={r} value={r}>
              {ROLE_LABELS[r]}
            </option>
          ))}
        </Select>
      </Field>
    </Modal>
  );
}
