// ---- Ticket ----
export interface Office {
  id?: string;
  name: string;
  address: string;
  city: string;
}

export interface Manager {
  full_name: string;
  role: string;
}

export interface CreateTicketRequest {
  raw_text: string;
  user_channel?: string;
}

export interface CreateTicketResponse {
  ticket_id: string;
  status: string;
  office?: Office;
  manager?: Manager;
}

export interface TicketStatusResponse {
  ticket_id: string;
  status: string;
  created_at?: string;
  raw_text?: string;
  sentiment?: string;
  recommendation?: string;
  normalized_address?: string;
  office?: Office;
  manager?: Manager;
  user_response_json?: Record<string, unknown>;
  ai_analysis?: Record<string, unknown>;
  assignment_reason?: string;
  summary?: string;
  city?: string;
  request_type?: string;
  priority?: string;
}

// ---- Auth ----
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface SpecialistProfile {
  id: string;
  full_name: string;
  username: string;
  role: string;
  office_id?: string;
}

// ---- Specialist ----
export interface TicketListItem {
  ticket_id: string;
  created_at: string;
  status: string;
  summary: string;
  city: string;
  request_type: string;
  priority: string;
}

export interface TicketDetail extends TicketListItem {
  raw_text: string;
  ai_analysis?: Record<string, unknown>;
  assignment_reason?: string;
}

export interface AssistantRequest {
  message: string;
}

export interface AssistantResponse {
  answer: string;
  thread_id: string;
}

// ---- Admin ----
export interface CreateOfficeRequest {
  name: string;
  address: string;
  city: string;
}

export interface CreateSpecialistRequest {
  full_name: string;
  username: string;
  password: string;
  role: string;
  office_id: string;
}

// ---- Health ----
export interface HealthResponse {
  status: string;
  [key: string]: unknown;
}

// ---- Chat ----
export interface ChatMessage {
  role: "specialist" | "assistant" | "user";
  content: string;
}

// ---- Backend Tools ----
export interface BackendBootstrapResponse {
  offices: number;
  managers: number;
}

export interface BackendProcessOneRequest {
  payload: Record<string, unknown>;
}

export interface BackendProcessOneResponse {
  ticket: Record<string, unknown>;
}

export interface BackendProcessCsvResponse {
  count: number;
  tickets: Record<string, unknown>[];
}

export interface BackendRecentResponse {
  items: Record<string, unknown>[];
}
