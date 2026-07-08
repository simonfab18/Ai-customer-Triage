# Security and Data Controls

## Secret and Token Lifecycle

Production and staging secrets must live in the hosting/provider secret store, not in source control or frontend bundles.

Required rotation procedure:

1. Create the replacement secret in the provider dashboard.
2. Deploy the API and worker with both the new secret value and incremented `ENCRYPTION_KEY_VERSION` where applicable.
3. Reconnect Gmail accounts that enter `reauthorization_required`.
4. Confirm `/v1/orgs/{organization_id}/gmail/connections` shows the new `token_key_version` for reconnected accounts.
5. Remove the old secret only after no active connection depends on it.

Current limitation: encrypted Gmail refresh tokens are versioned with `token_key_version`, but automatic bulk re-encryption is not implemented yet. Rotation is therefore supported through reconnect/re-authorization until a multi-key decrypt-and-reencrypt job is added.

## Gmail Reauthorization

When Google rejects a refresh token as revoked or invalid, the backend marks the Gmail connection as:

```text
status = reauthorization_required
sync_status = reauthorization_required
watch_status = reauthorization_required
sync_error_code = reauthorization_required
```

The connection is recoverable by starting Gmail OAuth again for the same Google account. Reauthorization clears the error state and stores the new token using the current `ENCRYPTION_KEY_VERSION`.

## Gmail Disconnect Semantics

Disconnecting Gmail marks the connection as revoked/disconnected and stops sync/watch operations. Existing tickets, audit logs, triage results, reply approvals, and Gmail draft records remain in the application for continuity and auditability.

Disconnect does not delete imported email content. Organization deletion/export controls are required before real production customers can self-serve data removal.

## Organization Export Direction

Until a self-serve export endpoint exists, exports should be handled as an operator-run procedure:

1. Verify requester identity and owner/admin role.
2. Export organization-scoped records only: organization, members, customers, tickets, ticket events, audit logs, Gmail connection metadata, sync events, AI triage results, reply suggestions/approvals, and draft metadata.
3. Exclude encrypted refresh tokens and provider access tokens.
4. Deliver exports through a secure, expiring channel.
5. Record the export in audit logs.

## Organization Deletion Direction

Deletion must be explicit, audited, and delayed enough to prevent accidental loss.

Recommended future behavior:

1. Disable Gmail sync and revoke active connections.
2. Soft-delete or archive the organization immediately.
3. Queue hard deletion for organization-scoped data after a retention window.
4. Preserve minimal billing/security/audit records only where legally required.
5. Verify backups age out according to the backup-retention policy.

## Retention Policy

Initial pilot policy direction:

- Ticket email bodies: retain while the organization is active.
- Gmail sync events and job runs: retain operational history for at least 90 days.
- Audit logs: retain for at least 1 year during pilot unless legal requirements differ.
- AI prompts/outputs: retain only what is needed for ticket auditability and troubleshooting.
- Attachments: not imported by default; add an explicit attachment policy before enabling attachment ingestion.

## Backup and Restore

Before pilot launch:

1. Confirm database backup schedule and retention in the managed database provider.
2. Restore the latest staging backup into an isolated staging database.
3. Run migrations against the restored database.
4. Verify organization list, tickets, audit logs, Gmail connection metadata, and operations status load correctly.
5. Record restore date, operator, source backup, and result.

## Frontend Secret Boundary

Frontend bundles must never include service-role keys, Gmail client secrets, Gemini API keys, encrypted refresh tokens, raw refresh tokens, internal operations tokens, or database URLs.
