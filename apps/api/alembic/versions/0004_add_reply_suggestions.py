"""add reply suggestions

Revision ID: 0004_add_reply_suggestions
Revises: 0003_add_ticket_queue_indexes
Create Date: 2026-07-05 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0004_add_reply_suggestions"
down_revision: str | None = "0003_add_ticket_queue_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reply_suggestions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("ai_triage_result_id", sa.String(length=36), nullable=True),
        sa.Column("gmail_connection_id", sa.String(length=36), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("edited_body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_by", sa.String(length=20), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=120), nullable=True),
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
    for column in [
        "ai_triage_result_id",
        "approved_by_user_id",
        "created_at",
        "created_by_user_id",
        "gmail_connection_id",
        "organization_id",
        "status",
        "ticket_id",
    ]:
        op.create_index(f"ix_reply_suggestions_{column}", "reply_suggestions", [column])


def downgrade() -> None:
    for column in [
        "ai_triage_result_id",
        "approved_by_user_id",
        "created_at",
        "created_by_user_id",
        "gmail_connection_id",
        "organization_id",
        "status",
        "ticket_id",
    ]:
        op.drop_index(f"ix_reply_suggestions_{column}", table_name="reply_suggestions")
    op.drop_table("reply_suggestions")