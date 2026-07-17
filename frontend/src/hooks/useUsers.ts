import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { UsersService, type UserPatch } from "@/client";
import { unwrap } from "@/lib/api";
import { qk } from "@/lib/queryKeys";

export function useUsers(enabled = true) {
  return useQuery({
    queryKey: qk.users,
    queryFn: () => unwrap(UsersService.usersGetUsers()),
    enabled,
  });
}

export function useUserMutations() {
  const qc = useQueryClient();

  const updateRole = useMutation({
    mutationFn: ({ id, body }: { id: number; body: UserPatch }) =>
      unwrap(UsersService.usersUpdateUser({ path: { user_id: id }, body })),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.users });
      qc.invalidateQueries({ queryKey: qk.me });
    },
  });

  return { updateRole };
}
