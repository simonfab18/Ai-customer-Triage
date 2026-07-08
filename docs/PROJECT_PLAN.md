# Project Plan

## Current Stage

The project is past the initial MVP foundation. The app now has a Next.js frontend, FastAPI backend, Supabase-backed PostgreSQL database, Supabase Auth, Gmail OAuth, Gmail import, AI triage with Gemini, reply approvals, Gmail draft creation, dashboard views, role-aware navigation, and local development servers.

Security and tenant hardening is now implemented locally. The next major production milestone is M7: staging and pilot release, which will prove the full Gmail-to-draft workflow against production-like infrastructure.

## Completed Milestones

### Milestone 1: Foundation

- Created monorepo structure.
- Added Next.js frontend with TypeScript.
- Added FastAPI backend.
- Added Docker Compose support for API, Redis, and worker.
- Added environment templates.
- Added health check endpoint.
- Added basic CI workflow.

### Milestone 2: Database and Auth Foundation

- Connected the backend to Supabase PostgreSQL.
- Added Supabase Auth integration.
- Added authenticated user context.
- Added organization and membership models.
- Added owner, admin, and agent role concepts.

### Milestone 3: Organizations and Role Isolation

- Added organization creation and selection.
- Added member management.
- Added role-based access checks.
- Added multi-tenant organization scoping across core resources.

### Milestone 4: Gmail OAuth

- Added Gmail OAuth connect flow.
- Added encrypted refresh token storage.
- Added OAuth state validation.
- Added Gmail connection status in the UI.

### Milestone 5: Gmail Import

- Added Gmail import endpoint.
- Added import job tracking.
- Added ticket creation from Gmail messages.
- Added duplicate message protection by Gmail message ID.
- Added recent import status in the UI.

### Milestone 6: AI Triage

- Added Gemini-powered ticket triage.
- Added structured AI output validation.
- Added category, priority, sentiment, summary, suggested action, draft reply, confidence, reasoning, and human review flag.
- Added triage results to ticket detail.

### Milestone 7: Human Reply Review

- Added reply suggestions.
- Added agent editing.
- Added approve and reject actions.
- Added status lifecycle: suggested, edited, approved, rejected, draft_created.
- Added ticket events for approval actions.

### Milestone 8: Gmail Draft Creation

- Added approved-reply Gmail draft creation.
- Stored Gmail draft IDs.
- Prevented duplicate draft creation.
- Updated ticket state after draft creation.
- Exposed draft result in the UI.

### Milestone 9: Audit and Security Hardening

- Added audit logs for important actions.
- Added endpoint to view organization audit logs.
- Added safer error responses.
- Ensured sensitive Gmail token fields are not returned by API responses.
- Added organization authorization checks for key resources.


### Production M0: Release Baseline

- Added validated staging and production environment settings.
- Added migration upgrade/downgrade validation in CI.
- Added frontend lint, typecheck, production build, and container build checks.
- Documented release, rollback, environment separation, and ownership controls.

### Production M1: Live Gmail Sync Foundation

- Added Gmail watch registration after OAuth connection.
- Added Gmail watch renewal service and worker task entrypoint.
- Added Gmail watch and sync state fields to Gmail connections.
- Added `gmail_sync_events` for watch registration, renewal, and Pub/Sub notification records.
- Added authenticated Pub/Sub webhook foundation at `POST /v1/webhooks/google/gmail`.
- Documented Google Cloud Pub/Sub project, topic, subscription, push endpoint, and service-account settings.
- Confirmed M1 stopped at authenticated notification receipt; history-based ticket ingestion was completed in M2.

### Production M2: Incremental Sync and Recovery

- Added Gmail history-list processing from stored checkpoints.
- Added duplicate-safe ticket creation for new `messagesAdded` notifications.
- Added per-connection sync locks to avoid concurrent duplicate processing.
- Added Pub/Sub webhook job enqueue and duplicate delivery handling.
- Added expired-checkpoint reconciliation with watch re-registration.
- Added stale-connection fallback sync discovery.
- Added owner/admin sync status and manual history-sync queue endpoints.



### Production M3: Automatic Triage Pipeline

- Added automatic AI triage job enqueue after manual ticket creation, manual Gmail import, and Gmail history sync ticket creation.
- Added ticket triage states for queued, running, succeeded, and failed triage.
- Added one-active-job idempotency for each ticket.
- Added prompt/schema version and latency metadata to AI triage results.
- Added worker execution for AI triage jobs.
- Added visible failure state and manual retry endpoint.
- Added workspace setting support for disabling automatic triage.
### Production M4: Core Workflow Polish

- Added centralized ticket lifecycle transition validation.
- Added `awaiting_approval` lifecycle state after successful triage.
- Added reply version tracking for approvals and suggestions.
- Editing approved replies now invalidates approval and requires reapproval.
- Draft creation now checks the latest approved reply version.
- Repeated Gmail draft creation is idempotent and returns the existing draft.
- Closed tickets cannot create Gmail drafts.
- Ticket list endpoints now support limit and offset pagination.

### Production M5: Operations and Observability

- Expanded job-run tracking with queue, attempts, timing, related resources, correlation IDs, retry eligibility, error classification, alert owner, and runbook metadata.
- Added owner/admin operations endpoints for recent workspace failures, job detail, safe retry, and Gmail sync health.
- Added a token-protected internal operations endpoint for system-wide failed jobs.
- Added structured JSON request and worker logging with safe request/job/resource context.
- Added sanitized error handling so tokens, authorization headers, email bodies, and prompts are not written to normal logs.
- Added `/health/live`, `/health/ready`, and richer `/v1/status` dependency reporting.
- Added tests for operations access, retry behavior, sync-health redaction, and health/status checks.
### Production M6: Security and Tenant Hardening

- Added authorization matrix coverage for owner/admin-only surfaces, agent workflow surfaces, disabled members, and cross-organization resource IDs.
- Tightened audit-log access to owner/admin users.
- Added rate limiting for OAuth, Gmail sync/watch, triage, retry, draft creation, and member invitation actions.
- Added request body-size protection and standard API security headers.
- Added Gmail token key-version metadata and recoverable `reauthorization_required` state for revoked refresh tokens.
- Added redaction hardening for structured logs and operational errors.
- Documented secret rotation, reauthorization, data export/deletion direction, retention, backup/restore, and attachment policy.
### Product UI Pass

- Added modern SaaS-style landing page.
- Added app shell with sidebar navigation.
- Added pages for overview, inbox, approvals, customers, analytics, integrations, workspace, team, and settings.
- Added responsive layout direction.
- Added reusable product UI components for badges, cards, queue rows, and app navigation.

## Next Recommended Milestone: M7 Staging and Pilot Release

### Goal

The complete Gmail-to-draft workflow should be proven in a production-like staging environment before a real pilot inbox is connected.

### Recommended Production Design

- Use separate staging infrastructure for database, Redis, deployed API/worker, Google OAuth, Pub/Sub, Gmail test inbox, and Gemini.
- Run the full Gmail notification-to-draft workflow outside local services.
- Add an E2E release suite covering workspace creation, Gmail connection, sync, triage, approval, draft creation, audit, disconnect, reconnect, and missed-notification recovery.
- Add pilot controls such as feature flags, allowlisted organizations, and kill switches for sync, triage, and draft creation.

### Backend Work

- Configure staging services and environment variables.
- Add and run E2E tests against staging-like dependencies.
- Verify scheduler, worker, Redis, migrations, Pub/Sub, Gmail, Gemini, and rollback procedures.
- Add pilot kill switches and allowlist controls where they are missing.

### Frontend Work

- Add staging-facing UI checks for Gmail connect, sync health, triage, approval, draft creation, disconnect, and reconnect.
- Ensure pilot controls are visible to owner/admin users.
- Confirm no mock/demo data appears in production-like dashboards.
## Later Milestones

### Knowledge and Automation

- Add reusable response templates.
- Add company policy or knowledge base snippets.
- Allow AI replies to use workspace knowledge.
- Add routing or assignment rules.

### Analytics

- Response time trends.
- Triage volume by urgency.
- AI confidence distribution.
- Draft approval rate.
- Agent workload.

### Production Readiness

- Rotate all exposed development secrets.
- Confirm staging and production environment variables.
- Confirm deployed Google OAuth redirect URLs.
- Confirm deployed CORS origins.
- Confirm Render worker and Redis are running.
- Run full end-to-end staging test.
