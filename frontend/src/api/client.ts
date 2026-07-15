import type {
  AdminUser,
  DashboardSummary,
  EventInfo,
  PaginatedRegistrations,
  RegistrationDetail,
  RegistrationPayload,
  RegistrationResult
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
};

export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function csrfToken(): string | undefined {
  const match = document.cookie.match(new RegExp("(^| )abn_csrf_token=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : undefined;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { ...(options.headers ?? {}) };
  let body: BodyInit | undefined;
  if (options.body instanceof FormData) {
    body = options.body;
  } else if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(options.body);
  }
  if (["POST", "PATCH", "PUT", "DELETE"].includes(options.method ?? "GET")) {
    const token = csrfToken();
    if (token) headers["X-CSRF-Token"] = token;
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: options.method ?? "GET",
      headers,
      body,
      credentials: "include",
      signal: controller.signal
    });
    const text = await response.text();
    const data = text ? JSON.parse(text) : {};
    if (!response.ok) {
      const error = data?.error ?? {};
      throw new ApiError(response.status, error.code ?? "REQUEST_FAILED", error.message ?? "Request failed.", error.details);
    }
    return data as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(408, "REQUEST_TIMEOUT", "The request timed out. Please try again.");
    }
    throw new ApiError(0, "NETWORK_ERROR", "Unable to reach the server. Please check your connection.");
  } finally {
    window.clearTimeout(timeout);
  }
}

export const publicApi = {
  event: () => request<EventInfo>("/api/public/event"),
  register: (payload: RegistrationPayload, idempotencyKey: string) =>
    request<RegistrationResult>("/api/public/registrations", {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: {
        ...payload,
        age: Number(payload.age),
        email: payload.email.trim() || null,
        educational_qualification: payload.educational_qualification.trim() || null,
        additional_contact_number: payload.additional_contact_number.trim() || null,
        studied_standard: payload.alpha_alumni === "Yes" ? payload.studied_standard.trim() : null,
        year_of_passing: payload.alpha_alumni === "Yes" ? payload.year_of_passing.trim() : null,
        consent_given: true
      }
    })
};

export const adminApi = {
  login: (email: string, password: string) =>
    request<{ success: boolean; user: AdminUser }>("/api/admin/auth/login", { method: "POST", body: { email, password } }),
  logout: () => request<{ success: boolean }>("/api/admin/auth/logout", { method: "POST" }),
  me: () => request<AdminUser>("/api/admin/auth/me"),
  summary: () => request<DashboardSummary>("/api/admin/dashboard/summary"),
  registrations: (query: URLSearchParams) => request<PaginatedRegistrations>(`/api/admin/registrations?${query.toString()}`),
  registration: (id: string) => request<RegistrationDetail>(`/api/admin/registrations/${id}`),
  updateRegistration: (id: string, body: Partial<RegistrationDetail>) =>
    request<RegistrationDetail>(`/api/admin/registrations/${id}`, { method: "PATCH", body }),
  updateStatus: (id: string, registration_status: string, admin_notes?: string | null) =>
    request<RegistrationDetail>(`/api/admin/registrations/${id}/status`, {
      method: "PATCH",
      body: { registration_status, admin_notes }
    }),
  retryEmail: (id: string) => request<RegistrationDetail>(`/api/admin/registrations/${id}/retry-email`, { method: "POST" }),
  retrySheet: (id: string) => request<RegistrationDetail>(`/api/admin/registrations/${id}/retry-sheet-sync`, { method: "POST" }),
  event: () => request<EventInfo>("/api/admin/event"),
  updateEvent: (body: Partial<EventInfo>) => request<EventInfo>("/api/admin/event", { method: "PATCH", body }),
  previewImport: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<{ success: boolean; columns: string[]; total_rows: number; sample_rows: Record<string, string>[]; rows: Record<string, string>[] }>(
      "/api/admin/registrations/import/preview",
      { method: "POST", body }
    );
  },
  confirmImport: (rows: Record<string, string>[], mapping: Record<string, string>, skip_duplicates = true) =>
    request("/api/admin/registrations/import/confirm", { method: "POST", body: { rows, mapping, skip_duplicates } })
};

export function exportUrl(type: "csv" | "xlsx", query: URLSearchParams): string {
  return `${API_BASE}/api/admin/registrations/export/${type}?${query.toString()}`;
}
