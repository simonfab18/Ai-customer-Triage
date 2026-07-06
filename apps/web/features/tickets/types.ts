export type TicketListItem = {
  id: string;
  customer_email: string;
  customer_name: string | null;
  gmail_message_id: string | null;
  gmail_thread_id: string | null;
  subject: string;
  status: string;
  category: string;
  priority: string;
  sentiment: string;
  assigned_to_user_id: string | null;
  received_at: string;
  updated_at: string;
};

export type Ticket = TicketListItem & {
  organization_id: string;
  customer_id: string;
  customer: {
    id: string;
    email: string;
    name: string | null;
  };
  message_text: string;
  message_html: string | null;
  created_at: string;
};

export type TicketEvent = {
  id: string;
  organization_id: string;
  ticket_id: string;
  actor_user_id: string | null;
  event_type: string;
  event_metadata: Record<string, unknown>;
  created_at: string;
};

export type AITriageResult = {
  id: string;
  organization_id: string;
  ticket_id: string;
  model_provider: string;
  model_name: string;
  category: string;
  priority: string;
  sentiment: string;
  summary: string;
  suggested_action: string;
  draft_reply: string;
  requires_human_review: boolean;
  validation_status: string;
  created_at: string;
};

export type ReplySuggestion = {
  id: string;
  organization_id: string;
  ticket_id: string;
  ai_triage_result_id: string | null;
  gmail_connection_id: string | null;
  body: string;
  edited_body: string | null;
  status: "suggested" | "edited" | "approved" | "rejected" | "draft_created" | string;
  created_by: "ai" | "agent" | string;
  created_by_user_id: string | null;
  approved_by_user_id: string | null;
  approved_at: string | null;
  gmail_draft_id: string | null;
  created_at: string;
  updated_at: string;
};

export type GmailDraft = {
  id: string;
  organization_id: string;
  ticket_id: string;
  reply_suggestion_id: string;
  gmail_draft_id: string;
  gmail_thread_id: string | null;
  created_by_user_id: string;
  created_at: string;
};

export type GmailDraftCreateResponse = {
  approval: ReplySuggestion;
  draft: GmailDraft;
  gmail_draft_id: string;
};

export type MetricsOverview = {
  total_tickets: number;
  active_tickets: number;
  resolved_tickets: number;
  spam_tickets: number;
  critical_tickets: number;
  high_priority_tickets: number;
  draft_created_tickets: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
};