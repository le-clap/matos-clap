import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  CatalogsService,
  CategoriesService,
  ItemsService,
  type Availability,
  type CatalogPatch,
  type CatalogPost,
  type CategoryPatch,
  type CategoryPost,
  type Condition,
  type ItemPatch,
  type ItemPost,
} from '@/client';
import { unwrap } from '@/lib/api';
import { qk } from '@/lib/queryKeys';

/* ------------------------------- Categories ------------------------------- */

export function useCategories() {
  return useQuery({
    queryKey: qk.categories,
    queryFn: () => unwrap(CategoriesService.categoriesGetCategories()),
  });
}

export function useCategoryMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: qk.categories });
    qc.invalidateQueries({ queryKey: qk.catalogs });
  };

  const create = useMutation({
    mutationFn: (body: CategoryPost) =>
      unwrap(CategoriesService.categoriesCreateCategory({ body })),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ id, body }: { id: number; body: CategoryPatch }) =>
      unwrap(
        CategoriesService.categoriesUpdateCategory({
          path: { category_id: id },
          body,
        }),
      ),
    onSuccess: invalidate,
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      unwrap(
        CategoriesService.categoriesDeleteCategory({
          path: { category_id: id },
        }),
      ),
    onSuccess: invalidate,
  });

  return { create, update, remove };
}

/* -------------------------------- Catalogs -------------------------------- */

export function useCatalogs() {
  return useQuery({
    queryKey: qk.catalogs,
    queryFn: () => unwrap(CatalogsService.catalogsGetCatalogs()),
  });
}

export function useCatalog(id: number) {
  return useQuery({
    queryKey: qk.catalog(id),
    queryFn: () => unwrap(CatalogsService.catalogsGetCatalogById({ path: { catalog_id: id } })),
    enabled: Number.isFinite(id),
  });
}

export function useCatalogAvailability(
  id: number,
  startIso: string,
  endIso: string,
  enabled = true,
) {
  return useQuery({
    queryKey: qk.catalogAvailability(id, startIso, endIso),
    queryFn: () =>
      unwrap(
        CatalogsService.catalogsGetCatalogItemsAvailability({
          path: { catalog_id: id },
          query: { start_date: startIso, end_date: endIso },
        }),
      ),
    enabled: enabled && Number.isFinite(id) && !!startIso && !!endIso,
  });
}

export function useCatalogMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: qk.catalogs });

  const create = useMutation({
    mutationFn: (body: CatalogPost) => unwrap(CatalogsService.catalogsCreateCatalog({ body })),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ id, body }: { id: number; body: CatalogPatch }) =>
      unwrap(
        CatalogsService.catalogsUpdateCatalog({
          path: { catalog_id: id },
          body,
        }),
      ),
    onSuccess: invalidate,
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      unwrap(CatalogsService.catalogsDeleteCatalog({ path: { catalog_id: id } })),
    onSuccess: invalidate,
  });
  const uploadImage = useMutation({
    mutationFn: ({ id, file }: { id: number; file: File }) =>
      unwrap(
        CatalogsService.catalogsUploadCatalogImage({
          path: { catalog_id: id },
          body: { file },
        }),
      ),
    onSuccess: invalidate,
  });

  return { create, update, remove, uploadImage };
}

/* ---------------------------------- Items --------------------------------- */

export function useItems(filters?: { availability?: Availability; condition?: Condition }) {
  return useQuery({
    queryKey: qk.items(filters),
    queryFn: () =>
      unwrap(
        ItemsService.itemsGetItems({
          query: {
            availability: filters?.availability ?? null,
            condition: filters?.condition ?? null,
          },
        }),
      ),
  });
}

export function useItemHistory(id: number, enabled = true) {
  return useQuery({
    queryKey: qk.itemHistory(id),
    queryFn: () => unwrap(ItemsService.itemsGetItemHistory({ path: { item_id: id } })),
    enabled: enabled && Number.isFinite(id),
  });
}

export function useItemMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['items'] });
    qc.invalidateQueries({ queryKey: qk.catalogs });
  };

  const create = useMutation({
    mutationFn: (body: ItemPost) => unwrap(ItemsService.itemsCreateItem({ body })),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ id, body }: { id: number; body: ItemPatch }) =>
      unwrap(ItemsService.itemsUpdateItem({ path: { item_id: id }, body })),
    onSuccess: invalidate,
  });
  const remove = useMutation({
    mutationFn: (id: number) => unwrap(ItemsService.itemsSoftDeleteItem({ path: { item_id: id } })),
    onSuccess: invalidate,
  });

  return { create, update, remove };
}
