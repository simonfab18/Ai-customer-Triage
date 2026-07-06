export type Organization = {
  id: string;
  name: string;
  slug: string;
  role: string;
};

export type MeResponse = {
  id: string;
  email: string | null;
  organizations: Organization[];
};

export type GmailConnection = {
  id: string;
  organization_id: string;
  connected_by_user_id: string;
  gmail_email: string;
  google_account_id: string;
  scopes: string;
  status: string;
  last_sync_at: string | null;
  created_at: string;
  updated_at: string;
};

export type JobRun = {
  id: string;
  organization_id: string;
  job_type: string;
  status: string;
  error_message: string | null;
  job_metadata: Record<string, unknown>;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
};

export type Member = {
  id: string;
  organization_id: string;
  user_id: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
};