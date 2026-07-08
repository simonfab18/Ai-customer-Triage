# Project Plan

## Current Stage

The project is past the initial MVP foundation. The app now has a Next.js frontend, FastAPI backend, Supabase-backed PostgreSQL database, Supabase Auth, Gmail OAuth, Gmail import, AI triage with Gemini, reply approvals, Gmail draft creation, dashboard views, role-aware navigation, and local development servers.

Core workflow polish is now implemented locally. The next major product improvement is M5: operations and observability, which will make failures visible, retryable, and alertable.

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

### Product UI Pass

- Added modern SaaS-style landing page.
- Added app shell with sidebar navigation.
- Added pages for overview, inbox, approvals, customers, analytics, integrations, workspace, team, and settings.
- Added responsive layout direction.
- Added reusable product UI components for badges, cards, queue rows, and app navigation.

## Next Recommended Milestone: M5 Operations and Observability

### Goal

Operational failures should be visible, traceable, retryable, and alertable without relying on ad hoc log inspection.

### Recommended Production Design

- Track job runs with attempts, timing, related resources, and sanitized errors.
- Add structured request and worker logging with correlation IDs.
- Surface recent failures to owner/admin users and internal operators.
- Define retry eligibility for Gmail, Gemini, Redis, and database failures.
- Add health/readiness signals for API, worker, queue, and dependencies.

### Backend Work

- Expand job-run model and retry metadata where needed.
- Add operations/status endpoints for recent failed jobs and sync health.
- Add structured logging context and error classification.
- Add tests for retryable and terminal failure states.

### Frontend Work

- Add owner/admin operational status surfaces.
- Show retryable failures with clear next actions.
- Avoid exposing sensitive provider or tenant internals.
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

