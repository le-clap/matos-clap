import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  RequestsService,
  type RequestPatch,
  type RequestPost,
  type RequestStatus,
} from "@/client";
import { unwrap } from "@/lib/api";
import { qk } from "@/lib/queryKeys";

export interface RequestFilters {
  borrowerId?: number;
  processed?: boolean;
  page?: number;
  limit?: number;
}

export function useRequests(filters: RequestFilters = {}) {
  const { borrowerId, processed, page = 0, limit = 20 } = filters;
  return useQuery({
    queryKey: qk.requests({ borrowerId, processed, page, limit }),
    queryFn: () =>
      unwrap(
        RequestsService.requestsGetRequests({
          query: {
            borrower_id: borrowerId ?? null,
            processed: processed ?? null,
            page,
            limit,
          },
        }),
      ),
  });
}

export function useRequest(id: number) {
  return useQuery({
    queryKey: qk.request(id),
    queryFn: () =>
      unwrap(
        RequestsService.requestsGetRequestById({ path: { request_id: id } }),
      ),
    enabled: Number.isFinite(id),
  });
}

export function useRequestRecommendations(id: number, enabled = true) {
  return useQuery({
    queryKey: qk.recommendations(id),
    queryFn: () =>
      unwrap(
        RequestsService.requestsGetRequestRecommendations({
          path: { request_id: id },
        }),
      ),
    enabled: enabled && Number.isFinite(id),
  });
}

export function useRequestMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["requests"] });

  const create = useMutation({
    mutationFn: (body: RequestPost) =>
      unwrap(RequestsService.requestsCreateRequest({ body })),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ id, body }: { id: number; body: RequestPatch }) =>
      unwrap(
        RequestsService.requestsUpdateRequest({
          path: { request_id: id },
          body,
        }),
      ),
    onSuccess: invalidate,
  });
  const setStatus = useMutation({
  mutationFn: ({id, status,}: { id: number; status: RequestStatus; }) =>
    unwrap(
      RequestsService.requestsUpdateRequest({
        path: { request_id: id },
        body: { status },
      }),
    ),
  onSuccess: invalidate,
});
  const remove = useMutation({
    mutationFn: (id: number) =>
      unwrap(
        RequestsService.requestsDeleteRequest({ path: { request_id: id } }),
      ),
    onSuccess: invalidate,
  });

  return { create, update, setStatus, remove };
}
