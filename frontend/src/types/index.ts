// ─── Shared TypeScript types ──────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'clinician' | 'viewer';
  specialty?: string;
  created_at: string;
}

export interface Citation {
  source_id: string;
  title: string;
  source_type: string;
  authors?: string;
  publication_date?: string;
  url?: string;
  relevance_score: number;
  snippet: string;
}

export interface QueryResponse {
  query_id: string;
  query: string;
  response: string;
  citations: Citation[];
  query_type: string;
  confidence_score?: number;
  processing_time_ms: number;
  timestamp: string;
}

export interface QueryHistoryItem {
  query_id: string;
  query: string;
  response_preview: string;
  query_type: string;
  timestamp: string;
  citation_count: number;
}

export interface Diagnosis {
  condition: string;
  likelihood: 'High' | 'Medium' | 'Low';
  confidence_score: number;
  supporting_evidence: string[];
  recommended_tests?: string[];
  citations: Citation[];
}

export interface DiagnosticResponse {
  session_id: string;
  stage: 'gathering' | 'reasoning' | 'refining' | 'complete';
  message: string;
  follow_up_question?: string;
  differential_diagnoses?: Diagnosis[];
  is_complete: boolean;
  timestamp: string;
}

export interface IngestResponse {
  status: string;
  documents_processed: number;
  chunks_created: number;
  errors: string[];
  processing_time_ms: number;
}

export interface HealthStatus {
  status: string;
  version: string;
  services: Record<string, string>;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}
