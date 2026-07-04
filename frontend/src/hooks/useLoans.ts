import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  LoansService,
  type LoanPartialReturnPost,
  type LoanPatch,
  type LoanPost,
  type LoanReturnPost,
} from "@/client";
import { unwrap } from "@/lib/api";
import { qk } from "@/lib/queryKeys";

export interface LoanFilters {
  borrowerId?: number;
  active?: boolean;
  page?: number;
  limit?: number;
}

export function useLoans(filters: LoanFilters = {}) {
  const { borrowerId, active, page = 0, limit = 20 } = filters;
  return useQuery({
    queryKey: qk.loans({ borrowerId, active, page, limit }),
    queryFn: () =>
      unwrap(
        LoansService.loansGetLoans({
          query: {
            borrower_id: borrowerId ?? null,
            active: active ?? null,
            page,
            limit,
          },
        }),
      ),
  });
}

export function useLoan(id: number) {
  return useQuery({
    queryKey: qk.loan(id),
    queryFn: () =>
      unwrap(LoansService.loansGetLoanById({ path: { loan_id: id } })),
    enabled: Number.isFinite(id),
  });
}

export function useLoanTimeline(startIso: string, endIso: string, enabled = true) {
  return useQuery({
    queryKey: qk.loansTimeline(startIso, endIso),
    queryFn: () =>
      unwrap(
        LoansService.loansGetLoansTimeline({
          query: { start_date: startIso, end_date: endIso },
        }),
      ),
    enabled: enabled && !!startIso && !!endIso,
  });
}

export function useLoanMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["loans"] });
    qc.invalidateQueries({ queryKey: ["items"] });
    qc.invalidateQueries({ queryKey: ["requests"] });
  };

  const create = useMutation({
    mutationFn: (body: LoanPost) =>
      unwrap(LoansService.loansCreateLoan({ body })),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ id, body }: { id: number; body: LoanPatch }) =>
      unwrap(LoansService.loansUpdateLoan({ path: { loan_id: id }, body })),
    onSuccess: invalidate,
  });
  const returnLoan = useMutation({
    mutationFn: ({ id, body }: { id: number; body: LoanReturnPost }) =>
      unwrap(LoansService.loansReturnLoan({ path: { loan_id: id }, body })),
    onSuccess: invalidate,
  });
  const partialReturn = useMutation({
    mutationFn: ({ id, body }: { id: number; body: LoanPartialReturnPost }) =>
      unwrap(
        LoansService.loansPartialReturnLoanItems({
          path: { loan_id: id },
          body,
        }),
      ),
    onSuccess: invalidate,
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      unwrap(LoansService.loansDeleteLoan({ path: { loan_id: id } })),
    onSuccess: invalidate,
  });

  return { create, update, returnLoan, partialReturn, remove };
}
