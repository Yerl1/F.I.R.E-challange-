import type {
  TicketListItem,
  TicketDetail,
  CreateTicketResponse,
  TicketStatusResponse,
  SpecialistProfile,
  HealthResponse,
} from "./types";

export const MOCK_TICKETS: TicketListItem[] = [
  {
    ticket_id: "TK-001",
    created_at: "2026-02-20T10:30:00Z",
    status: "DONE",
    summary: "Request for mortgage consultation in Almaty branch",
    city: "Almaty",
    request_type: "Mortgage",
    priority: "HIGH",
  },
  {
    ticket_id: "TK-002",
    created_at: "2026-02-20T11:15:00Z",
    status: "PROCESSING",
    summary: "VIP client complaint about card transaction fees",
    city: "Astana",
    request_type: "Complaint",
    priority: "URGENT",
  },
  {
    ticket_id: "TK-003",
    created_at: "2026-02-19T14:45:00Z",
    status: "DONE",
    summary: "Business account opening inquiry for SME",
    city: "Shymkent",
    request_type: "Account Opening",
    priority: "MEDIUM",
  },
  {
    ticket_id: "TK-004",
    created_at: "2026-02-19T09:00:00Z",
    status: "DONE",
    summary: "Currency exchange rate consultation request",
    city: "Almaty",
    request_type: "Consultation",
    priority: "LOW",
  },
  {
    ticket_id: "TK-005",
    created_at: "2026-02-18T16:20:00Z",
    status: "PROCESSING",
    summary: "Insurance product inquiry for family plan",
    city: "Aktau",
    request_type: "Insurance",
    priority: "MEDIUM",
  },
];

export const MOCK_TICKET_DETAIL: TicketDetail = {
  ticket_id: "TK-001",
  created_at: "2026-02-20T10:30:00Z",
  status: "DONE",
  summary: "Request for mortgage consultation in Almaty branch",
  city: "Almaty",
  request_type: "Mortgage",
  priority: "HIGH",
  raw_text:
    "Hello, I would like to apply for a mortgage loan for an apartment in Almaty. My budget is around 35 million tenge. I have a stable income and have been employed for 5 years. Could you please assign me to the nearest branch and a specialist who handles mortgage applications?",
  ai_analysis: {
    intent: "mortgage_application",
    detected_city: "Almaty",
    detected_product: "Mortgage Loan",
    sentiment: "positive",
    urgency: "medium",
    language: "en",
    key_entities: ["35M tenge budget", "5 years employment", "apartment"],
  },
  assignment_reason:
    "Client requests mortgage consultation. Routed to Almaty Central Branch based on detected city. Assigned to senior mortgage specialist via round-robin allocation. High priority due to high-value product request.",
};

export const MOCK_CREATE_RESPONSE: CreateTicketResponse = {
  ticket_id: "TK-006",
  status: "DONE",
  office: {
    name: "Almaty Central Branch",
    address: "123 Abay Avenue, Almaty",
    city: "Almaty",
  },
  manager: {
    full_name: "Aisha Nurlanovna",
    role: "Senior Mortgage Specialist",
  },
};

export const MOCK_TICKET_STATUS: TicketStatusResponse = {
  ticket_id: "TK-001",
  status: "DONE",
  created_at: "2026-02-20T10:30:00Z",
  office: {
    name: "Almaty Central Branch",
    address: "123 Abay Avenue, Almaty",
    city: "Almaty",
  },
  manager: {
    full_name: "Aisha Nurlanovna",
    role: "Senior Mortgage Specialist",
  },
};

export const MOCK_PROFILE: SpecialistProfile = {
  id: "sp-001",
  full_name: "Damir Kasenov",
  username: "d.kasenov",
  role: "Senior Support Specialist",
  office_id: "off-001",
};

export const MOCK_HEALTH: HealthResponse = {
  status: "OK",
  version: "1.4.2",
  uptime: "14d 6h 32m",
  database: "connected",
};

export const MOCK_OFFICES = [
  { id: "off-001", name: "Almaty Central Branch", address: "123 Abay Avenue, Almaty", city: "Almaty" },
  { id: "off-002", name: "Astana Main Office", address: "45 Mangilik El, Astana", city: "Astana" },
  { id: "off-003", name: "Shymkent Service Center", address: "78 Tauke Khan, Shymkent", city: "Shymkent" },
];
