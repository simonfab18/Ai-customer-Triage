"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-05 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gmail_oauth_states",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=240), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gmail_oauth_states_organization_id", "gmail_oauth_states", ["organization_id"])
    op.create_index("ix_gmail_oauth_states_state", "gmail_oauth_states", ["state"], unique=True)
    op.create_index("ix_gmail_oauth_states_user_id", "gmail_oauth_states", ["user_id"])

    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", name="uq_customer_org_email"),
    )
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_index("ix_customers_organization_id", "customers", ["organization_id"])

    op.create_table(
        "gmail_connections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("connected_by_user_id", sa.String(length=120), nullable=False),
        sa.Column("gmail_email", sa.String(length=320), nullable=False),
        sa.Column("google_account_id", sa.String(length=160), nullable=False),
        sa.Column("encrypted_refresh_token", sa.String(length=2048), nullable=False),
        sa.Column("access_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gmail_connections_connected_by_user_id", "gmail_connections", ["connected_by_user_id"])
    op.create_index("ix_gmail_connections_google_account_id", "gmail_connections", ["google_account_id"])
    op.create_index("ix_gmail_connections_organization_id", "gmail_connections", ["organization_id"])
    op.create_index("ix_gmail_connections_status", "gmail_connections", ["status"])

    op.create_table(
        "job_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("job_metadata", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_runs_created_at", "job_runs", ["created_at"])
    op.create_index("ix_job_runs_job_type", "job_runs", ["job_type"])
    op.create_index("ix_job_runs_organization_id", "job_runs", ["organization_id"])

    op.create_table(
        "organization_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_member_user"),
    )
    op.create_index("ix_organization_members_organization_id", "organization_members", ["organization_id"])
    op.create_index("ix_organization_members_user_id", "organization_members", ["user_id"])

    op.create_table(
        "mail_import_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("gmail_connection_id", sa.String(length=36), nullable=False),
        sa.Column("support_label_id", sa.String(length=120), nullable=True),
        sa.Column("processed_label_id", sa.String(length=120), nullable=True),
        sa.Column("spam_label_id", sa.String(length=120), nullable=True),
        sa.Column("import_unread_only", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["gmail_connection_id"], ["gmail_connections.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mail_import_rules_gmail_connection_id", "mail_import_rules", ["gmail_connection_id"], unique=True)
    op.create_index("ix_mail_import_rules_organization_id", "mail_import_rules", ["organization_id"])

    op.create_table(
        "tickets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("gmail_connection_id", sa.String(length=36), nullable=True),
        sa.Column("gmail_message_id", sa.String(length=160), nullable=True),
        sa.Column("gmail_thread_id", sa.String(length=160), nullable=True),
        sa.Column("subject", sa.String(length=300), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("message_html", sa.Text(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("sentiment", sa.String(length=20), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["gmail_connection_id"], ["gmail_connections.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "gmail_message_id", name="uq_ticket_org_gmail_message"),
    )
    for column in ["assigned_to_user_id", "category", "customer_id", "gmail_connection_id", "gmail_message_id", "gmail_thread_id", "organization_id", "priority", "received_at", "status"]:
        op.create_index(f"ix_tickets_{column}", "tickets", [column])

    op.create_table(
        "ai_triage_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("model_provider", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("raw_input", sa.JSON(), nullable=False),
        sa.Column("raw_output", sa.JSON(), nullable=False),
        sa.Column("validated_output", sa.JSON(), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("sentiment", sa.String(length=20), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("draft_reply", sa.Text(), nullable=False),
        sa.Column("requires_human_review", sa.Boolean(), nullable=False),
        sa.Column("validation_status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_triage_results_created_at", "ai_triage_results", ["created_at"])
    op.create_index("ix_ai_triage_results_organization_id", "ai_triage_results", ["organization_id"])
    op.create_index("ix_ai_triage_results_ticket_id", "ai_triage_results", ["ticket_id"])

    op.create_table(
        "ticket_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=120), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ["actor_user_id", "created_at", "event_type", "organization_id", "ticket_id"]:
        op.create_index(f"ix_ticket_events_{column}", "ticket_events", [column])

    op.create_table(
        "reply_approvals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("ai_triage_result_id", sa.String(length=36), nullable=False),
        sa.Column("gmail_connection_id", sa.String(length=36), nullable=True),
        sa.Column("suggested_reply", sa.Text(), nullable=False),
        sa.Column("final_reply", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("approved_by_user_id", sa.String(length=120), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gmail_draft_id", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ai_triage_result_id"], ["ai_triage_results.id"]),
        sa.ForeignKeyConstraint(["gmail_connection_id"], ["gmail_connections.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ["ai_triage_result_id", "approved_by_user_id", "created_at", "gmail_connection_id", "organization_id", "status", "ticket_id"]:
        op.create_index(f"ix_reply_approvals_{column}", "reply_approvals", [column])

    op.create_table(
        "gmail_drafts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("reply_suggestion_id", sa.String(length=36), nullable=False),
        sa.Column("gmail_draft_id", sa.String(length=160), nullable=False),
        sa.Column("gmail_thread_id", sa.String(length=160), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "reply_suggestion_id", name="uq_gmail_draft_org_suggestion"),
    )
    for column in ["created_at", "created_by_user_id", "gmail_draft_id", "gmail_thread_id", "organization_id", "reply_suggestion_id", "ticket_id"]:
        op.create_index(f"ix_gmail_drafts_{column}", "gmail_drafts", [column])


def downgrade() -> None:
    for table, columns in [
        ("gmail_drafts", ["created_at", "created_by_user_id", "gmail_draft_id", "gmail_thread_id", "organization_id", "reply_suggestion_id", "ticket_id"]),
        ("reply_approvals", ["ai_triage_result_id", "approved_by_user_id", "created_at", "gmail_connection_id", "organization_id", "status", "ticket_id"]),
        ("ticket_events", ["actor_user_id", "created_at", "event_type", "organization_id", "ticket_id"]),
    ]:
        for column in columns:
            op.drop_index(f"ix_{table}_{column}", table_name=table)
        op.drop_table(table)

    op.drop_index("ix_ai_triage_results_ticket_id", table_name="ai_triage_results")
    op.drop_index("ix_ai_triage_results_organization_id", table_name="ai_triage_results")
    op.drop_index("ix_ai_triage_results_created_at", table_name="ai_triage_results")
    op.drop_table("ai_triage_results")

    for column in ["assigned_to_user_id", "category", "customer_id", "gmail_connection_id", "gmail_message_id", "gmail_thread_id", "organization_id", "priority", "received_at", "status"]:
        op.drop_index(f"ix_tickets_{column}", table_name="tickets")
    op.drop_table("tickets")

    op.drop_index("ix_mail_import_rules_organization_id", table_name="mail_import_rules")
    op.drop_index("ix_mail_import_rules_gmail_connection_id", table_name="mail_import_rules")
    op.drop_table("mail_import_rules")

    op.drop_index("ix_organization_members_user_id", table_name="organization_members")
    op.drop_index("ix_organization_members_organization_id", table_name="organization_members")
    op.drop_table("organization_members")

    op.drop_index("ix_job_runs_organization_id", table_name="job_runs")
    op.drop_index("ix_job_runs_job_type", table_name="job_runs")
    op.drop_index("ix_job_runs_created_at", table_name="job_runs")
    op.drop_table("job_runs")

    for name in ["status", "organization_id", "google_account_id", "connected_by_user_id"]:
        op.drop_index(f"ix_gmail_connections_{name}", table_name="gmail_connections")
    op.drop_table("gmail_connections")

    op.drop_index("ix_customers_organization_id", table_name="customers")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_table("customers")

    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")

    op.drop_index("ix_gmail_oauth_states_user_id", table_name="gmail_oauth_states")
    op.drop_index("ix_gmail_oauth_states_state", table_name="gmail_oauth_states")
    op.drop_index("ix_gmail_oauth_states_organization_id", table_name="gmail_oauth_states")
    op.drop_table("gmail_oauth_states")