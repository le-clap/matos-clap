/** Centralised TanStack Query keys. */
export const qk = {
  me: ["me"] as const,

  categories: ["categories"] as const,
  category: (id: number) => ["categories", id] as const,

  catalogs: ["catalogs"] as const,
  catalog: (id: number) => ["catalogs", id] as const,
  catalogAvailability: (id: number, start: string, end: string) =>
    ["catalogs", id, "availability", start, end] as const,

  items: (filters?: Record<string, unknown>) => ["items", filters ?? {}] as const,
  item: (id: number) => ["items", "detail", id] as const,
  itemHistory: (id: number) => ["items", "history", id] as const,
  loanedItems: (start: string, end: string) =>
    ["items", "loaned", start, end] as const,

  loans: (filters?: Record<string, unknown>) => ["loans", filters ?? {}] as const,
  loan: (id: number) => ["loans", "detail", id] as const,
  loansTimeline: (start: string, end: string) =>
    ["loans", "timeline", start, end] as const,

  requests: (filters?: Record<string, unknown>) =>
    ["requests", filters ?? {}] as const,
  request: (id: number) => ["requests", "detail", id] as const,
  recommendations: (id: number) => ["requests", id, "recommendations"] as const,

  users: (filters?: Record<string, unknown>) => ["users", filters ?? {}] as const,
  user: (id: number) => ["users", id] as const,
};
