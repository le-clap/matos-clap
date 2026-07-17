import { ApiError } from "./api";

/** Download a CSV from an authenticated endpoint and trigger a file save. */
export async function downloadCsv(path: string, filename: string): Promise<void> {
  const res = await fetch(path, { credentials: "include" });
  if (!res.ok) throw new ApiError(res.status, "Échec de l'export");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export type ImportResult =
  | { ok: true; created: number; updated: number }
  | { ok: false; errors: string[] };

/** Upload a CSV for import. Returns row-level errors instead of throwing. */
export async function importCsv(path: string, file: File): Promise<ImportResult> {
  const body = new FormData();
  body.append("file", file);
  const res = await fetch(path, { method: "POST", credentials: "include", body });
  const data = await res.json().catch(() => null);

  if (res.ok) {
    return { ok: true, created: data?.created ?? 0, updated: data?.updated ?? 0 };
  }
  const detail = data?.detail;
  const errors = Array.isArray(detail)
    ? detail.map(String)
    : [detail ? String(detail) : `Erreur ${res.status}`];
  return { ok: false, errors };
}
