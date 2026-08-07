import type { LoanPublic } from '@/client';

/** Whether a loan is overdue (active and past its planned end date). */
export function isOverdue(loan: LoanPublic): boolean {
  return loan.status === 'active' && new Date(loan.end_date) < new Date();
}
