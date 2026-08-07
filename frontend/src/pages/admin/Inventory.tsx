import { History, Image as ImageIcon, ImagePlus, Pencil, Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';
import type { Availability, CatalogPublic, CategoryPublic, Condition, ItemPublic } from '@/client';
import { PageHeader } from '@/components/PageHeader';
import { Button } from '@/components/ui/Button';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { EmptyState } from '@/components/ui/EmptyState';
import { Field } from '@/components/ui/Field';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { Skeleton } from '@/components/ui/Skeleton';
import { AvailabilityBadge, ConditionBadge } from '@/components/ui/StatusBadge';
import { Table, TBody, Td, Th, THead, Tr } from '@/components/ui/Table';
import { Tabs } from '@/components/ui/Tabs';
import { useToast } from '@/components/ui/Toast';
import { ImportExportButtons } from '@/features/inventory/ImportExportButtons';
import { ItemHistoryModal } from '@/features/inventory/ItemHistoryModal';
import {
  useCatalogMutations,
  useCatalogs,
  useCategories,
  useCategoryMutations,
  useItemMutations,
  useItems,
} from '@/hooks/useInventory';
import { ApiError } from '@/lib/api';
import { formatMoney } from '@/lib/format';

type Tab = 'catalogs' | 'categories' | 'items';

export function AdminInventoryPage() {
  const [tab, setTab] = useState<Tab>('catalogs');
  const catalogs = useCatalogs();
  const categories = useCategories();
  const items = useItems();

  return (
    <div>
      <PageHeader
        title="Inventaire"
        description="Gérez les catégories, le catalogue et les articles physiques."
      />
      <div className="mb-4">
        <Tabs
          value={tab}
          onChange={setTab}
          items={[
            { value: 'catalogs', label: 'Catalogue', count: catalogs.data?.length },
            { value: 'categories', label: 'Catégories', count: categories.data?.length },
            { value: 'items', label: 'Articles', count: items.data?.length },
          ]}
        />
      </div>

      {tab === 'catalogs' && <CatalogsTab />}
      {tab === 'categories' && <CategoriesTab />}
      {tab === 'items' && <ItemsTab />}
    </div>
  );
}

/* -------------------------------- Catalogs -------------------------------- */

function CatalogsTab() {
  const { data, isLoading } = useCatalogs();
  const { data: categories } = useCategories();
  const { create, update, remove, uploadImage } = useCatalogMutations();
  const toast = useToast();
  const [editing, setEditing] = useState<CatalogPublic | 'new' | null>(null);
  const [toDelete, setToDelete] = useState<CatalogPublic | null>(null);

  return (
    <Section
      onAdd={() => setEditing('new')}
      addLabel="Nouvelle référence"
      leading={<ImportExportButtons entity="catalogs" />}
      empty={!isLoading && (!data || data.length === 0)}
      loading={isLoading}
    >
      <Table>
        <THead>
          <Tr>
            <Th>Nom</Th>
            <Th>Catégorie</Th>
            <Th>Description</Th>
            <Th className="w-px" />
          </Tr>
        </THead>
        <TBody>
          {data?.map((c) => (
            <Tr key={c.id}>
              <Td className="font-medium">{c.name}</Td>
              <Td className="text-content-muted">{c.category.name}</Td>
              <Td className="max-w-xs truncate text-content-muted">{c.description ?? '—'}</Td>
              <Td>
                <RowActions onEdit={() => setEditing(c)} onDelete={() => setToDelete(c)} />
              </Td>
            </Tr>
          ))}
        </TBody>
      </Table>

      {editing && (
        <CatalogModal
          catalog={editing === 'new' ? null : editing}
          categories={categories ?? []}
          saving={create.isPending || update.isPending || uploadImage.isPending}
          onClose={() => setEditing(null)}
          onSave={async (body, file, removeImage) => {
            let catalogId: number;
            if (editing === 'new') {
              catalogId = (await create.mutateAsync(body)).id;
            } else {
              // Clearing the image is a patch of image_path → null.
              const patch = removeImage && !file ? { ...body, image_path: null } : body;
              await update.mutateAsync({ id: editing.id, body: patch });
              catalogId = editing.id;
            }
            if (file) await uploadImage.mutateAsync({ id: catalogId, file });
            toast.success(editing === 'new' ? 'Référence créée' : 'Référence mise à jour');
            setEditing(null);
          }}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        onClose={() => setToDelete(null)}
        loading={remove.isPending}
        title="Supprimer la référence ?"
        description={`« ${toDelete?.name} » sera supprimée. Les références contenant des articles ne peuvent pas être supprimées.`}
        confirmLabel="Supprimer"
        onConfirm={async () => {
          try {
            await remove.mutateAsync(toDelete!.id);
            toast.success('Référence supprimée');
            setToDelete(null);
          } catch (err) {
            toast.error('Suppression impossible', err instanceof ApiError ? err.detail : undefined);
            setToDelete(null);
          }
        }}
      />
    </Section>
  );
}

function CatalogModal({
  catalog,
  categories,
  onClose,
  onSave,
  saving,
}: {
  catalog: CatalogPublic | null;
  categories: CategoryPublic[];
  onClose: () => void;
  onSave: (
    body: {
      name: string;
      description: string | null;
      category_id: number;
    },
    file: File | null,
    removeImage: boolean,
  ) => void;
  saving: boolean;
}) {
  const [name, setName] = useState(catalog?.name ?? '');
  const [description, setDescription] = useState(catalog?.description ?? '');
  const [categoryId, setCategoryId] = useState(catalog?.category.id ?? categories[0]?.id ?? 0);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(catalog?.image_path ?? null);
  const [removeImage, setRemoveImage] = useState(false);

  const onPick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0] ?? null;
    setFile(picked);
    setRemoveImage(false);
    if (picked) setPreview(URL.createObjectURL(picked));
  };

  const onRemove = () => {
    setFile(null);
    setPreview(null);
    setRemoveImage(true);
  };

  return (
    <Modal
      open
      onClose={onClose}
      title={catalog ? 'Modifier la référence' : 'Nouvelle référence'}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            disabled={!name.trim() || !categoryId}
            onClick={() =>
              onSave(
                {
                  name: name.trim(),
                  description: description.trim() || null,
                  category_id: categoryId,
                },
                file,
                removeImage,
              )
            }
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <Field label="Image">
          <div className="flex items-center gap-3">
            <div className="size-20 shrink-0 overflow-hidden rounded-lg border border-border bg-surface-raised">
              {preview ? (
                <img src={preview} alt="" className="size-full object-cover" />
              ) : (
                <div className="flex size-full items-center justify-center text-content-faint">
                  <ImageIcon className="size-6" />
                </div>
              )}
            </div>
            <label className="inline-flex h-9 cursor-pointer items-center gap-2 rounded-lg border border-border bg-surface-raised px-3 text-sm font-medium text-content transition-colors hover:bg-surface-hover">
              <ImagePlus className="size-4" />
              {preview ? "Changer l'image" : 'Choisir une image'}
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                className="hidden"
                onChange={onPick}
              />
            </label>
            {preview && (
              <button
                type="button"
                onClick={onRemove}
                className="inline-flex h-9 items-center gap-1.5 rounded-lg px-2.5 text-sm font-medium text-content-faint transition-colors hover:bg-danger-bg hover:text-brand-300"
              >
                <Trash2 className="size-4" />
                Supprimer
              </button>
            )}
          </div>
        </Field>
        <Field label="Nom" required>
          <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </Field>
        <Field label="Catégorie" required>
          <Select value={categoryId} onChange={(e) => setCategoryId(Number(e.target.value))}>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Description">
          <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
        </Field>
      </div>
    </Modal>
  );
}

/* ------------------------------- Categories ------------------------------- */

function CategoriesTab() {
  const { data, isLoading } = useCategories();
  const { create, update, remove } = useCategoryMutations();
  const toast = useToast();
  const [editing, setEditing] = useState<CategoryPublic | 'new' | null>(null);
  const [toDelete, setToDelete] = useState<CategoryPublic | null>(null);

  return (
    <Section
      onAdd={() => setEditing('new')}
      addLabel="Nouvelle catégorie"
      leading={<ImportExportButtons entity="categories" />}
      empty={!isLoading && (!data || data.length === 0)}
      loading={isLoading}
    >
      <Table>
        <THead>
          <Tr>
            <Th>Nom</Th>
            <Th>Description</Th>
            <Th className="w-px" />
          </Tr>
        </THead>
        <TBody>
          {data?.map((c) => (
            <Tr key={c.id}>
              <Td className="font-medium">{c.name}</Td>
              <Td className="max-w-md truncate text-content-muted">{c.description ?? '—'}</Td>
              <Td>
                <RowActions onEdit={() => setEditing(c)} onDelete={() => setToDelete(c)} />
              </Td>
            </Tr>
          ))}
        </TBody>
      </Table>

      {editing && (
        <CategoryModal
          category={editing === 'new' ? null : editing}
          saving={create.isPending || update.isPending}
          onClose={() => setEditing(null)}
          onSave={async (body) => {
            if (editing === 'new') {
              await create.mutateAsync(body);
              toast.success('Catégorie créée');
            } else {
              await update.mutateAsync({ id: editing.id, body });
              toast.success('Catégorie mise à jour');
            }
            setEditing(null);
          }}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        onClose={() => setToDelete(null)}
        loading={remove.isPending}
        title="Supprimer la catégorie ?"
        description={`« ${toDelete?.name} » sera supprimée. Les catégories contenant des références ne peuvent pas être supprimées.`}
        confirmLabel="Supprimer"
        onConfirm={async () => {
          try {
            await remove.mutateAsync(toDelete!.id);
            toast.success('Catégorie supprimée');
            setToDelete(null);
          } catch (err) {
            toast.error('Suppression impossible', err instanceof ApiError ? err.detail : undefined);
            setToDelete(null);
          }
        }}
      />
    </Section>
  );
}

function CategoryModal({
  category,
  onClose,
  onSave,
  saving,
}: {
  category: CategoryPublic | null;
  onClose: () => void;
  onSave: (body: { name: string; description: string | null }) => void;
  saving: boolean;
}) {
  const [name, setName] = useState(category?.name ?? '');
  const [description, setDescription] = useState(category?.description ?? '');

  return (
    <Modal
      open
      onClose={onClose}
      title={category ? 'Modifier la catégorie' : 'Nouvelle catégorie'}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            disabled={!name.trim()}
            onClick={() => onSave({ name: name.trim(), description: description.trim() || null })}
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <Field label="Nom" required>
          <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </Field>
        <Field label="Description">
          <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
        </Field>
      </div>
    </Modal>
  );
}

/* ---------------------------------- Items --------------------------------- */

const CONDITIONS: { value: Condition; label: string }[] = [
  { value: 'new', label: 'Neuf' },
  { value: 'good', label: 'Bon état' },
  { value: 'degraded', label: 'Dégradé' },
];
const AVAILABILITIES: { value: Availability; label: string }[] = [
  { value: 'available', label: 'Disponible' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'retired', label: 'Retiré' },
];

function ItemsTab() {
  const { data, isLoading } = useItems();
  const { data: catalogs } = useCatalogs();
  const { create, update, remove } = useItemMutations();
  const toast = useToast();
  const [editing, setEditing] = useState<ItemPublic | 'new' | null>(null);
  const [toDelete, setToDelete] = useState<ItemPublic | null>(null);
  const [history, setHistory] = useState<ItemPublic | null>(null);

  return (
    <Section
      onAdd={() => setEditing('new')}
      addLabel="Nouvel article"
      leading={<ImportExportButtons entity="items" />}
      empty={!isLoading && (!data || data.length === 0)}
      loading={isLoading}
    >
      <Table>
        <THead>
          <Tr>
            <Th>Article</Th>
            <Th>Référence</Th>
            <Th>État</Th>
            <Th>Statut</Th>
            <Th>Caution</Th>
            <Th className="w-px" />
          </Tr>
        </THead>
        <TBody>
          {data?.map((item) => (
            <Tr key={item.id}>
              <Td className="font-medium">{item.name}</Td>
              <Td className="text-content-muted">{item.catalog.name}</Td>
              <Td>
                <ConditionBadge condition={item.condition} />
              </Td>
              <Td>
                <AvailabilityBadge availability={item.availability} />
              </Td>
              <Td className="tabular-nums">
                {item.deposit_cents > 0 ? formatMoney(item.deposit_cents) : '—'}
              </Td>
              <Td>
                <RowActions
                  onHistory={() => setHistory(item)}
                  onEdit={() => setEditing(item)}
                  onDelete={() => setToDelete(item)}
                />
              </Td>
            </Tr>
          ))}
        </TBody>
      </Table>

      {editing && (
        <ItemModal
          item={editing === 'new' ? null : editing}
          catalogs={catalogs ?? []}
          saving={create.isPending || update.isPending}
          onClose={() => setEditing(null)}
          onSave={async (body, isNew) => {
            if (isNew) {
              await create.mutateAsync(body);
              toast.success('Article créé');
            } else {
              await update.mutateAsync({ id: (editing as ItemPublic).id, body });
              toast.success('Article mis à jour');
            }
            setEditing(null);
          }}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        onClose={() => setToDelete(null)}
        loading={remove.isPending}
        title="Supprimer l'article ?"
        description={`« ${toDelete?.name} » sera retirée de l'inventaire.`}
        confirmLabel="Supprimer"
        onConfirm={async () => {
          try {
            await remove.mutateAsync(toDelete!.id);
            toast.success('Article supprimé');
            setToDelete(null);
          } catch (err) {
            toast.error('Suppression impossible', err instanceof ApiError ? err.detail : undefined);
            setToDelete(null);
          }
        }}
      />

      <ItemHistoryModal item={history} onClose={() => setHistory(null)} />
    </Section>
  );
}

function ItemModal({
  item,
  catalogs,
  onClose,
  onSave,
  saving,
}: {
  item: ItemPublic | null;
  catalogs: CatalogPublic[];
  onClose: () => void;
  onSave: (
    body: {
      name: string;
      catalog_id: number;
      condition: Condition;
      availability: Availability;
      deposit_cents: number;
    },
    isNew: boolean,
  ) => void;
  saving: boolean;
}) {
  const [name, setName] = useState(item?.name ?? '');
  const [catalogId, setCatalogId] = useState(item?.catalog.id ?? catalogs[0]?.id ?? 0);
  const [condition, setCondition] = useState<Condition>(item?.condition ?? 'good');
  const [availability, setAvailability] = useState<Availability>(item?.availability ?? 'available');
  const [deposit, setDeposit] = useState(((item?.deposit_cents ?? 0) / 100).toFixed(2));

  return (
    <Modal
      open
      onClose={onClose}
      title={item ? "Modifier l'article" : 'Nouvel article'}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Annuler
          </Button>
          <Button
            loading={saving}
            disabled={!name.trim() || !catalogId}
            onClick={() =>
              onSave(
                {
                  name: name.trim(),
                  catalog_id: catalogId,
                  condition,
                  availability,
                  deposit_cents: Math.round(parseFloat(deposit || '0') * 100),
                },
                !item,
              )
            }
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <Field label="Nom" required hint="Identifiant de l'article, ex. « Canon R5 #2 »">
          <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </Field>
        <Field label="Référence" required>
          <Select value={catalogId} onChange={(e) => setCatalogId(Number(e.target.value))}>
            {catalogs.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="État">
            <Select value={condition} onChange={(e) => setCondition(e.target.value as Condition)}>
              {CONDITIONS.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Statut">
            <Select
              value={availability}
              onChange={(e) => setAvailability(e.target.value as Availability)}
            >
              {AVAILABILITIES.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </Select>
          </Field>
        </div>
        <Field label="Caution (€)">
          <Input
            type="number"
            min="0"
            step="0.01"
            value={deposit}
            onChange={(e) => setDeposit(e.target.value)}
          />
        </Field>
      </div>
    </Modal>
  );
}

/* -------------------------------- Shared --------------------------------- */

function Section({
  onAdd,
  addLabel,
  empty,
  loading,
  leading,
  children,
}: {
  onAdd: () => void;
  addLabel: string;
  empty: boolean;
  loading: boolean;
  leading?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>{leading}</div>
        <Button onClick={onAdd}>
          <Plus className="size-4" />
          {addLabel}
        </Button>
      </div>
      {loading ? (
        <Skeleton className="h-64 rounded-[var(--radius-card)]" />
      ) : empty ? (
        <EmptyState
          title="Rien ici pour le moment"
          description="Commencez par ajouter un élément."
          action={
            <Button onClick={onAdd}>
              <Plus className="size-4" />
              {addLabel}
            </Button>
          }
        />
      ) : (
        children
      )}
    </div>
  );
}

function RowActions({
  onEdit,
  onDelete,
  onHistory,
}: {
  onEdit: () => void;
  onDelete: () => void;
  onHistory?: () => void;
}) {
  return (
    <div className="flex items-center justify-end gap-1">
      {onHistory && (
        <Button variant="ghost" size="icon-sm" onClick={onHistory} aria-label="Historique">
          <History className="size-4" />
        </Button>
      )}
      <Button variant="ghost" size="icon-sm" onClick={onEdit} aria-label="Modifier">
        <Pencil className="size-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={onDelete}
        aria-label="Supprimer"
        className="text-content-faint hover:text-brand-300"
      >
        <Trash2 className="size-4" />
      </Button>
    </div>
  );
}
