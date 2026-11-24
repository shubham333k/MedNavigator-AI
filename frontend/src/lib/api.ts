// API client for the Healthcare Knowledge Navigator backend
import type {
  AuthTokens, QueryResponse, QueryHistoryItem,
  DiagnosticResponse, IngestResponse, HealthStatus,
} from '@/types';
import { clearAuth, getAccessToken, getRefreshToken, saveAuth } from '@/lib/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function redirectToLogin(): void {
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.assign('/login');
  }
}

// ─── Base fetch wrapper ──────────────────────────────────

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) {
      clearAuth();
      return null;
    }
    const tokens: AuthTokens = await response.json();
    saveAuth(tokens);
    return tokens.access_token;
  } catch {
    clearAuth();
    return null;
  }
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  allowRefresh = true,
): Promise<T> {
  const token = getAccessToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && allowRefresh && !path.startsWith('/api/auth/')) {
    const refreshedToken = await refreshAccessToken();
    if (refreshedToken) {
      return apiFetch<T>(path, options, false);
    }
    redirectToLogin();
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ─── Health ──────────────────────────────────────────────

export async function getHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>('/health');
}

// ─── Auth ────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<AuthTokens> {
  return apiFetch<AuthTokens>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, false);
}

export async function register(
  email: string,
  password: string,
  full_name: string,
  role: string = 'clinician',
  specialty?: string,
): Promise<AuthTokens> {
  return apiFetch<AuthTokens>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, role, specialty }),
  });
}

// ─── Query ───────────────────────────────────────────────

export async function queryKnowledgeBase(
  query: string,
  query_type: string = 'general',
  max_results: number = 5,
): Promise<QueryResponse> {
  return apiFetch<QueryResponse>('/api/query/', {
    method: 'POST',
    body: JSON.stringify({ query, query_type, max_results }),
  });
}

export async function getQueryHistory(limit = 20): Promise<QueryHistoryItem[]> {
  return apiFetch<QueryHistoryItem[]>(`/api/query/history?limit=${limit}`);
}

// ─── Diagnostic ──────────────────────────────────────────

export async function startDiagnostic(
  symptoms: string[],
  patient_age?: number,
  patient_sex?: string,
  medical_history?: string[],
  current_medications?: string[],
): Promise<DiagnosticResponse> {
  return apiFetch<DiagnosticResponse>('/api/diagnostic/start', {
    method: 'POST',
    body: JSON.stringify({
      symptoms,
      patient_age,
      patient_sex,
      medical_history,
      current_medications,
    }),
  });
}

export async function respondToDiagnostic(
  session_id: string,
  response: string,
): Promise<DiagnosticResponse> {
  return apiFetch<DiagnosticResponse>('/api/diagnostic/respond', {
    method: 'POST',
    body: JSON.stringify({ session_id, response }),
  });
}

// ─── Ingestion ───────────────────────────────────────────

export async function ingestSampleData(): Promise<IngestResponse> {
  return apiFetch<IngestResponse>('/api/ingest/sample-data', {
    method: 'POST',
  });
}

export async function ingestPubMed(
  query: string,
  max_results: number = 10,
): Promise<IngestResponse> {
  return apiFetch<IngestResponse>('/api/ingest/pubmed', {
    method: 'POST',
    body: JSON.stringify({ query, max_results }),
  });
}

export async function getIngestionStats(): Promise<{
  total_chunks: number;
  status: string;
  message: string;
}> {
  return apiFetch('/api/ingest/stats');
}

export async function uploadDocument(
  file: File,
  title: string,
  document_type: string,
  source_url?: string,
): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  formData.append('document_type', document_type);
  if (source_url) formData.append('source_url', source_url);

  const send = (token: string | null) => fetch(`${API_URL}/api/ingest/documents`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  let response = await send(getAccessToken());
  if (response.status === 401) {
    const refreshedToken = await refreshAccessToken();
    if (refreshedToken) response = await send(refreshedToken);
    else redirectToLogin();
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
