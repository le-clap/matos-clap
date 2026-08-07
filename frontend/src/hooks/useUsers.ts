import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { UsersService, type AccessLevel, type UserPatch } from '@/client';
import { unwrap } from '@/lib/api';
import { qk } from '@/lib/queryKeys';

export interface UserFilters {
  accessLevel?: AccessLevel;
  page?: number;
  limit?: number;
  search?: string;
}

export function useUsers(filters: UserFilters = {}, enabled = true) {
  const { accessLevel, page = 0, limit = 20, search } = filters;
  return useQuery({
    queryKey: qk.users({ accessLevel, page, limit, search }),
    queryFn: () =>
      unwrap(
        UsersService.usersGetUsers({
          query: {
            access_level: accessLevel ?? null,
            page,
            limit,
            search,
          },
        }),
      ),
    placeholderData: keepPreviousData,
    enabled,
  });
}

export function useUserMutations() {
  const qc = useQueryClient();

  const updateRole = useMutation({
    mutationFn: ({ id, body }: { id: number; body: UserPatch }) =>
      unwrap(UsersService.usersUpdateUser({ path: { user_id: id }, body })),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      qc.invalidateQueries({ queryKey: qk.me });
    },
  });

  return { updateRole };
}
