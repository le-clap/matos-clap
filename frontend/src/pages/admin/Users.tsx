import { ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";
import type { AccessLevel, UserPublic } from "@/client";
import { useAuth } from "@/auth/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import { SearchInput } from "@/components/ui/SearchInput";
import { Select } from "@/components/ui/Input";
import { Skeleton } from "@/components/ui/Skeleton";
import { Table, TBody, Td, Th, THead, Tr } from "@/components/ui/Table";
import { useToast } from "@/components/ui/Toast";
import { useUserMutations, useUsers } from "@/hooks/useUsers";
import { ROLE_LABELS, ROLE_ORDER } from "@/lib/roles";

const roleTone: Record<AccessLevel, Parameters<typeof Badge>[0]["tone"]> = {
  user: "neutral",
  clap: "info",
  manager: "warning",
  admin: "brand",
};

export function AdminUsersPage() {
  const { hasRole } = useAuth();
  const { data, isLoading } = useUsers();
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<UserPublic | null>(null);

  const canEdit = hasRole("admin");

  const rows = useMemo<UserPublic[]>((() => {
    if (!data?.items) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data.items;
    return data.items.filter(
      (u: UserPublic) =>
        u.name.toLowerCase().includes(q) ||
        u.username.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q),
    );
  }), [data, search]);

  return (
    <div>
      <PageHeader
        title="Utilisateurs"
        description={
          canEdit
            ? "Consultez les membres et gérez leurs rôles."
            : "Consultez les membres de la plateforme."
        }
        action={
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Rechercher…"
            className="w-56"
          />
        }
      />

      {isLoading ? (
        <Skeleton className="h-64 rounded-[var(--radius-card)]" />
      ) : (
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
                  <Badge tone={roleTone[u.access_level]}>
                    {ROLE_LABELS[u.access_level]}
                  </Badge>
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
      )}

      {editing && (
        <RoleModal user={editing} onClose={() => setEditing(null)} />
      )}
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
              toast.success("Rôle mis à jour");
              onClose();
            }}
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <Field label="Niveau d'accès">
        <Select
          value={role}
          onChange={(e) => setRole(e.target.value as AccessLevel)}
        >
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
