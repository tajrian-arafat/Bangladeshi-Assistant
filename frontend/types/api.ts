export type ConfidenceLevel = "high" | "medium" | "low" | "conflicted" | "unavailable";

export type ChecklistItemType =
  | "REQUIRED"
  | "OPTIONAL"
  | "CONDITIONAL"
  | "RECOMMENDED"
  | "NOT_APPLICABLE";

export interface ChecklistItem {
  item: string;
  type: ChecklistItemType;
  evidence_id?: string;
  confidence?: ConfidenceLevel;
}

export interface ProcedureStep {
  order: number;
  title: string;
  description?: string;
  official_url?: string | null;
}

export interface FeeItem {
  amount: string;
  currency: string;
  evidence_id?: string;
  label?: string;
}

export interface Citation {
  evidence_id: string;
  source_title: string;
  source_url: string;
  tier: number;
  last_verified_at: string;
  excerpt: string;
}

export interface ChatAnswer {
  summary: string;
  checklist?: ChecklistItem[];
  steps?: ProcedureStep[];
  fees?: FeeItem[];
  warnings?: string[];
  clarifications_needed?: ClarificationField[];
}

export interface ClarificationField {
  key: string;
  label: string;
  options?: { value: string; label: string }[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
  language_preference?: "auto" | "bn" | "en";
  clarifications?: Record<string, string>;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  language: string;
  confidence: ConfidenceLevel;
  answer: ChatAnswer;
  citations: Citation[];
  metadata?: {
    intent?: string;
    service_slug?: string;
    processing_ms?: number;
    llm_used?: boolean;
    fallback_mode?: boolean;
  };
}

export interface ServiceSummary {
  id: string;
  slug: string;
  name_en: string;
  name_bn: string;
  category?: string;
  status?: string;
  agency_id?: string;
}

export interface ServiceDetail extends ServiceSummary {
  aliases?: string[];
  eligibility?: Record<string, unknown>;
  checklist_items?: Array<{
    id: string;
    item_type: string;
    label_en: string;
    label_bn: string;
    order: number;
  }>;
  procedure_steps?: Array<{
    id: string;
    order: number;
    title_en: string;
    title_bn: string;
    description_en?: string;
    description_bn?: string;
    official_url?: string | null;
  }>;
  fees?: FeeItem[];
  last_verified_at?: string;
}

export interface District {
  id: string;
  slug: string;
  name_en: string;
  name_bn: string;
  division_name_en?: string;
  division_name_bn?: string;
}

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: ConfidenceLevel;
  answer?: ChatAnswer;
  citations?: Citation[];
  created_at?: string;
}

export interface Conversation {
  id: string;
  messages: ConversationMessage[];
}

export interface AdminLoginRequest {
  email: string;
  password: string;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface ReviewQueueItem {
  id: string;
  title: string;
  type: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  priority?: "high" | "medium" | "low";
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    correlation_id?: string;
    details?: Record<string, unknown>;
  };
}

export interface HealthStatus {
  status: string;
  version?: string;
}
