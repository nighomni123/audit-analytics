export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let message = response.statusText || `Request failed (${response.status})`;
  let code = "request_failed";
  let details: unknown;
  try {
    const body = (await response.json()) as {
      error?: { code?: string; message?: string; details?: unknown };
      detail?: string;
    };
    message = body.error?.message ?? body.detail ?? message;
    code = body.error?.code ?? code;
    details = body.error?.details;
  } catch {
    // Non-JSON failures retain the HTTP status text.
  }
  return new ApiError(message, response.status, code, details);
}

function apiPath(path: string): string {
  if (path.startsWith("/api/")) return path;
  return `/api${path.startsWith("/") ? path : `/${path}`}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiPath(path), init);
  if (!response.ok) throw await parseError(response);
  return (await response.json()) as T;
}

export function get<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export function put<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function upload<T>(path: string, form: FormData): Promise<T> {
  return request<T>(path, { method: "POST", body: form });
}

export async function download(path: string, body: unknown, filename: string): Promise<void> {
  const response = await fetch(apiPath(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw await parseError(response);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
