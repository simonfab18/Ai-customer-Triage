import { getApiBaseUrl } from "@/lib/config";
import type { GmailConnection, JobRun, MeResponse, Organization, Member } from "@/lib/api-types";

async function apiFetch<T>(path: string, accessToken: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export function getMe(accessToken: string) {
  return apiFetch<MeResponse>("/v1/me", accessToken);
}

export function createOrganization(accessToken: string, name: string) {
  return apiFetch<Organization>("/v1/organizations", accessToken, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function getGmailConnections(accessToken: string, organizationId: string) {
  return apiFetch<GmailConnection[]>(`/v1/orgs/${organizationId}/gmail/connections`, accessToken);
}

export function startGmailOAuth(accessToken: string, organizationId: string) {
  return apiFetch<{ auth_url: string; state: string }>(
    `/v1/orgs/${organizationId}/gmail/oauth/start`,
    accessToken,
  );
}

export function syncGmailConnection(accessToken: string, organizationId: string, connectionId: string) {
  return apiFetch<JobRun>(`/v1/orgs/${organizationId}/gmail/connections/${connectionId}/sync`, accessToken, {
    method: "POST",
    body: JSON.stringify({ max_results: 20 }),
  });
}

export function queueGmailSync(accessToken: string, organizationId: string, connectionId: string) {
  return apiFetch<JobRun>(`/v1/orgs/${organizationId}/gmail/connections/${connectionId}/sync/queue`, accessToken, {
    method: "POST",
    body: JSON.stringify({ max_results: 20 }),
  });
}

export function getRecentImports(accessToken: string, organizationId: string) {
  return apiFetch<JobRun[]>(`/v1/orgs/${organizationId}/imports/recent`, accessToken);
}

export function getJobRun(accessToken: string, organizationId: string, jobId: string) {
  return apiFetch<JobRun>(`/v1/orgs/${organizationId}/jobs/${jobId}`, accessToken);
}

export function getMembers(accessToken: string, organizationId: string) {
  return apiFetch<Member[]>(`/v1/orgs/${organizationId}/members`, accessToken);
}

export function inviteMember(accessToken: string, organizationId: string, email: string, role: string) {
  return apiFetch<Member>(`/v1/orgs/${organizationId}/members/invite`, accessToken, {
    method: "POST",
    body: JSON.stringify({ email, role }),
  });
}

export function updateMemberRole(accessToken: string, organizationId: string, memberId: string, role: string) {
  return apiFetch<Member>(`/v1/orgs/${organizationId}/members/${memberId}`, accessToken, {
    method: "PATCH",
    body: JSON.stringify({ role }),
  });
}