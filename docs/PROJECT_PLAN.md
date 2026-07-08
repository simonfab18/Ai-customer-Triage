# Project Plan

## Current Stage

The project is past the initial MVP foundation. The app now has a Next.js frontend, FastAPI backend, Supabase-backed PostgreSQL database, Supabase Auth, Gmail OAuth, Gmail import, AI triage with Gemini, reply approvals, Gmail draft creation, dashboard views, role-aware navigation, and local development servers.

The live Gmail sync foundation is now implemented. The next major product improvement is M2: incremental Gmail history sync and recovery, which will turn authenticated Gmail push notifications into duplicate-safe ticket ingestion.

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
- Confirmed M1 stops at authenticated notification receipt; history-based ticket ingestion remains M2.

### Product UI Pass

- Added modern SaaS-style landing page.
- Added app shell with sidebar navigation.
- Added pages for overview, inbox, approvals, customers, analytics, integrations, workspace, team, and settings.
- Added responsive layout direction.
- Added reusable product UI components for badges, cards, queue rows, and app navigation.

## Next Recommended Milestone: M2 Incremental Sync and Recovery

### Goal

Authenticated Gmail push notifications should trigger duplicate-safe Gmail history processing, create tickets for new matching messages, and recover safely from missed or expired checkpoints.

### Recommended Production Design

- Keep the manual import button as a fallback.
- Add Gmail Push Notifications through Google Cloud Pub/Sub.
- Store Gmail `historyId` per Gmail connection.
- Use `history.list` to import only new mailbox changes.
- Add a scheduled fallback sync because push notifications can be delayed or dropped.
- Renew Gmail watches daily because Gmail watches expire.

### Backend Work

- Add Gmail watch registration after connection.
- Add Pub/Sub webhook endpoint.
- Add job for processing Gmail notifications.
- Add history-based incremental import.
- Add scheduled watch renewal.
- Add scheduled fallback sync.

### Database Work

Add or extend Gmail connection tracking fields:

- `gmail_history_id`
- `watch_expires_at`
- `last_sync_at`
- `sync_status`
- `sync_error`

Optionally add a table for sync events:

- `gmail_sync_events`
- `organization_id`
- `gmail_connection_id`
- `event_type`
- `status`
- `metadata`
- `created_at`

### Frontend Work

- Show "Live sync active" on Integrations.
- Show "Last synced" beside inbox controls.
- Add a manual "Sync inbox" button.
- Show sync errors in a friendly way.

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

