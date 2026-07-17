import { client } from "@/client/client.gen";

/**
 * Configure the shared hey-api client:
 * - URLs are already absolute (`/api/...`), so no baseUrl is needed.
 * - `credentials: "include"` sends the httpOnly `session_id` cookie set by the
 *   CLA SSO callback.
 */
client.setConfig({
  credentials: "include",
});

export { client };

export class ApiError extends Error {
  status: number;
  detail?: string;
  constructor(status: number, detail?: string) {
    super(detail || `Erreur ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

interface RequestResult<T> {
  data?: T;
  error?: unknown;
  response: Response;
}

function extractDetail(error: unknown): string | undefined {
  if (!error || typeof error !== "object") return undefined;
  const detail = (error as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // FastAPI validation errors: [{ msg, loc, ... }]
    const first = detail[0] as { msg?: string } | undefined;
    return first?.msg;
  }
  return undefined;
}

/**
 * Await a hey-api SDK call and return its data, throwing a typed `ApiError`
 * on any non-2xx response. Lets TanStack Query handle errors uniformly.
 */
export async function unwrap<T>(promise: Promise<RequestResult<T>>): Promise<T> {
  const { data, error, response } = await promise;
  if (!response.ok || error !== undefined) {
    throw new ApiError(response.status, extractDetail(error));
  }
  return data as T;
}
