import type { AccessLevel } from "@/client";

/** Access levels from lowest to highest privilege. */
export const ROLE_ORDER: AccessLevel[] = [
  "user",
  "clap",
  "manager",
  "admin",
];

export const ROLE_LABELS: Record<AccessLevel, string> = {
  user: "Utilisateur",
  clap: "CLAP",
  manager: "Manager",
  admin: "Administrateur",
};

/** Whether `level` meets or exceeds `min`. */
export function hasRole(
  level: AccessLevel | undefined,
  min: AccessLevel,
): boolean {
  if (!level) return false;
  return ROLE_ORDER.indexOf(level) >= ROLE_ORDER.indexOf(min);
}
