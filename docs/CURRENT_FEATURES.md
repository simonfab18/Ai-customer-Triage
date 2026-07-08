# Current Features

This file reflects the latest local MVP state.

## Authentication

- Supabase Auth is used for user sign-up and sign-in.
- The frontend keeps the Supabase session.
- Backend requests are authenticated with bearer tokens.
- The backend resolves the current user through `/v1/me`.

## Organizations and Multi-Tenancy

- Users can create organizations.
- Users can belong to organizations as members.
- Core resources are scoped by `organization_id`.
- The app stores the selected organization on the frontend.
- Organization-specific resources include tickets, Gmail connections, imports, AI triage results, reply suggestions, Gmail drafts, audit logs, team members, and workspace settings.

## Roles

The system supports three roles:

- Owner
- Admin
- Agent

Owner/admin capabilities include workspace management, Gmail connection, and team administration. Agents focus on inbox, approvals, and ticket handling.

## Gmail Integration

- Owner/admin users can connect Gmail through OAuth 2.0.
- OAuth state is validated.
- Gmail refresh tokens are encrypted before storage.
- Gmail connection status can be viewed in the app.
- Gmail can be disconnected.
- Gmail import rules can be viewed and updated.
- Gmail watches can be registered after OAuth connection.
- Gmail watch renewal has a backend service and worker task entrypoint.
- Gmail connection responses include watch and sync status fields.
- Authenticated Google Pub/Sub push notifications can be accepted at `/v1/webhooks/google/gmail` and queued for Gmail history sync.
- Gmail history sync processes `messagesAdded` changes from stored checkpoints.
- Duplicate Gmail message IDs are skipped during live and manual import.
- Expired Gmail history checkpoints trigger bounded reconciliation and watch re-registration.
- Stale active connections can be discovered for fallback sync.
- Owner/admin users can view sync status and queue a manual history sync.

## Gmail Import

- Connected Gmail accounts can be manually imported.
- Imported Gmail messages are saved as tickets.
- Duplicate Gmail messages are skipped.
- Recent import jobs are shown in the UI.
- Import results include success, imported count, skipped count, and errors.

Current limitation:

- Live sync now queues Gmail history processing on the backend; UI polish for full sync health visibility remains part of a later operations/product pass.

## Tickets

- Tickets are created from imported Gmail messages.
- Tickets include subject, sender/customer, message text, Gmail message ID, Gmail thread ID, received time, status, category, priority, sentiment, and assigned user.
- Ticket statuses include:
  - new
  - open
  - pending
  - draft_created
  - resolved
  - spam
- Ticket priorities include:
  - critical
  - high
  - medium
  - low
- Tickets can be listed, searched, filtered, assigned, marked as spam, and resolved.
- Ticket detail shows the original email, AI result, reply suggestion, and lifecycle actions.

## AI Triage

- Gemini is used to classify support tickets.
- AI output is structured and validated.
- Triage result fields include:
  - category
  - priority
  - sentiment
  - summary
  - suggested action
  - draft reply
  - confidence score
  - reasoning
  - human review requirement
- Running triage updates the ticket classification fields.
- AI triage creates a reply suggestion for agent review.

## Reply Suggestions and Human Approval

- AI-generated replies are visible to agents.
- Agents can edit suggestions.
- Agents can approve suggestions.
- Agents can reject suggestions.
- Approved suggestions record the approving user and approval time.
- Rejected suggestions cannot be used for Gmail draft creation.
- Ticket events are written for important reply actions.

## Gmail Draft Creation

- Gmail drafts are created only from approved reply suggestions.
- Drafts are created in the related Gmail thread when possible.
- Gmail draft IDs are stored.
- Duplicate draft creation is blocked.
- Ticket status becomes `draft_created` after draft creation.
- The UI shows draft creation state/result.

## Dashboard and App UI

The app includes these main screens:

- Landing page
- Login page
- Overview dashboard
- Inbox
- Approvals
- Customers
- Analytics
- Gmail integrations/import
- Workspace settings
- Team and roles
- Settings

The UI uses a modern SaaS layout with:

- Sidebar navigation
- Top page context/actions
- Urgency-based ticket visuals
- Minimalist spacing
- Responsive page structure

## Metrics

The backend exposes organization metrics through:

- `GET /v1/orgs/{organization_id}/metrics/overview`

Metrics are used by the overview and analytics UI.

## Audit Logs

- Important organization actions can be written to audit logs.
- Audit logs include actor, action, resource type, resource ID, IP address, user agent, metadata, and timestamp.
- Audit logs are available through:
  - `GET /v1/orgs/{organization_id}/audit-logs`

## Workspace and Team

- Workspace settings can be viewed and updated.
- Team members can be listed.
- Owner/admin users can invite members.
- Owner/admin users can update member roles.
- Owner/admin users can remove members.

## Local Development

Current local links:

- Frontend: `http://localhost:3002`
- Backend health: `http://localhost:8001/health`

Current local mode uses manual server processes. Docker is available for API, Redis, and worker testing, but it is not required for everyday frontend/backend debugging.

