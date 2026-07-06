import type {
  AITriageResult,
  GmailDraftCreateResponse,
  MetricsOverview,
  ReplySuggestion,
  Ticket,
  TicketEvent,
  TicketListItem,
} from "./types";

function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

async function ticketApiFetch<T>(path: string, accessToken: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...(init.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function getMetricsOverview(organizationId: string, accessToken: string): Promise<MetricsOverview> {
  return ticketApiFetch<MetricsOverview>(`/v1/orgs/${organizationId}/metrics/overview`, accessToken);
}

export async function getTickets(organizationId: string, accessToken: string): Promise<TicketListItem[]> {
  return ticketApiFetch<TicketListItem[]>(`/v1/orgs/${organizationId}/tickets`, accessToken);
}

export async function getTicket(
  organizationId: string,
  ticketId: string,
  accessToken: string,
): Promise<Ticket> {
  return ticketApiFetch<Ticket>(`/v1/orgs/${organizationId}/tickets/${ticketId}`, accessToken);
}

export async function getTicketEvents(
  organizationId: string,
  ticketId: string,
  accessToken: string,
): Promise<TicketEvent[]> {
  return ticketApiFetch<TicketEvent[]>(`/v1/orgs/${organizationId}/tickets/${ticketId}/events`, accessToken);
}

export async function runTicketTriage(
  organizationId: string,
  ticketId: string,
  accessToken: string,
): Promise<AITriageResult> {
  return ticketApiFetch<AITriageResult>(`/v1/orgs/${organizationId}/tickets/${ticketId}/triage`, accessToken, {
    method: "POST",
  });
}

export async function getTicketTriageResults(
  organizationId: string,
  ticketId: string,
  accessToken: string,
): Promise<AITriageResult[]> {
  return ticketApiFetch<AITriageResult[]>(`/v1/orgs/${organizationId}/tickets/${ticketId}/triage-results`, accessToken);
}

export async function getReplySuggestions(
  organizationId: string,
  ticketId: string,
  accessToken: string,
): Promise<ReplySuggestion[]> {
  return ticketApiFetch<ReplySuggestion[]>(`/v1/orgs/${organizationId}/tickets/${ticketId}/reply-suggestions`, accessToken);
}

export async function updateReplySuggestion(
  organizationId: string,
  suggestionId: string,
  accessToken: string,
  editedBody: string,
): Promise<ReplySuggestion> {
  return ticketApiFetch<ReplySuggestion>(`/v1/orgs/${organizationId}/reply-suggestions/${suggestionId}`, accessToken, {
    method: "PATCH",
    body: JSON.stringify({ edited_body: editedBody }),
  });
}

export async function approveReplySuggestion(
  organizationId: string,
  suggestionId: string,
  accessToken: string,
): Promise<ReplySuggestion> {
  return ticketApiFetch<ReplySuggestion>(`/v1/orgs/${organizationId}/reply-suggestions/${suggestionId}/approve`, accessToken, {
    method: "POST",
  });
}

export async function rejectReplySuggestion(
  organizationId: string,
  suggestionId: string,
  accessToken: string,
): Promise<ReplySuggestion> {
  return ticketApiFetch<ReplySuggestion>(`/v1/orgs/${organizationId}/reply-suggestions/${suggestionId}/reject`, accessToken, {
    method: "POST",
  });
}

export async function createGmailDraftFromSuggestion(
  organizationId: string,
  suggestionId: string,
  accessToken: string,
): Promise<GmailDraftCreateResponse> {
  return ticketApiFetch<GmailDraftCreateResponse>(
    `/v1/orgs/${organizationId}/reply-suggestions/${suggestionId}/create-gmail-draft`,
    accessToken,
    { method: "POST" },
  );
}