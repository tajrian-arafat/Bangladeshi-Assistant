import type {
  AdminLoginRequest,
  AdminLoginResponse,
  ApiError,
  ChatRequest,
  ChatResponse,
  Conversation,
  District,
  HealthStatus,
  ReviewQueueItem,
  ServiceDetail,
  ServiceSummary,
} from "@/types/api";

const API_BASE =
  typeof window === "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : (process.env.NEXT_PUBLIC_API_URL ?? "");

export class ApiClientError extends Error {
  code: string;
  correlationId?: string;
  status: number;

  constructor(message: string, code: string, status: number, correlationId?: string) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.correlationId = correlationId;
  }
}

async function parseError(response: Response): Promise<ApiClientError> {
  let body: ApiError | null = null;
  try {
    body = (await response.json()) as ApiError;
  } catch {
    // ignore parse errors
  }

  return new ApiClientError(
    body?.error?.message ?? `Request failed with status ${response.status}`,
    body?.error?.code ?? "UNKNOWN_ERROR",
    response.status,
    body?.error?.correlation_id,
  );
}

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("bda_admin_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...getAuthHeaders(),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  health: () => request<HealthStatus>("/api/v1/health"),

  chat: (body: ChatRequest) =>
    request<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getConversation: (id: string) =>
    request<Conversation>(`/api/v1/conversations/${id}`),

  getServices: async (params?: { q?: string; category?: string }) => {
    const search = new URLSearchParams();
    if (params?.q) search.set("q", params.q);
    if (params?.category) search.set("category", params.category);
    const qs = search.toString();
    const response = await request<{ items: ServiceSummary[] }>(
      `/api/v1/services${qs ? `?${qs}` : ""}`,
    );
    return response.items;
  },

  getService: (slug: string) =>
    request<ServiceDetail>(`/api/v1/services/${slug}`),

  getDistricts: async () => {
    const response = await request<{ items: District[] }>("/api/v1/districts");
    return response.items;
  },

  search: (q: string) =>
    request<{ results: ServiceSummary[] }>(
      `/api/v1/search?q=${encodeURIComponent(q)}`,
    ),

  submitFeedback: (body: {
    message_id: string;
    rating: "helpful" | "not_helpful";
    comment?: string;
  }) =>
    request<void>("/api/v1/feedback", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  adminLogin: (body: AdminLoginRequest) =>
    request<AdminLoginResponse>("/api/v1/admin/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  adminDashboard: () =>
    request<{
      services_count: number;
      pending_reviews: number;
      sources_count: number;
      health: string;
    }>("/api/v1/admin/dashboard"),

  adminServices: () =>
    request<ServiceSummary[]>("/api/v1/admin/services"),

  adminReviews: () =>
    request<ReviewQueueItem[]>("/api/v1/admin/reviews"),
};

export { API_BASE };
