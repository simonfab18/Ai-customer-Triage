"""add ai confidence and workspace settings

Revision ID: 0005_ai_conf_workspace
Revises: 0004_add_reply_suggestions
Create Date: 2026-07-06 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0005_ai_conf_workspace"
down_revision: str | None = "0004_add_reply_suggestions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ai_triage_results", sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ai_triage_results", sa.Column("reasoning", sa.Text(), nullable=False, server_default=""))

    op.create_table(
        "workspace_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("default_reply_signature", sa.Text(), nullable=False),
        sa.Column("auto_triage_enabled", sa.Boolean(), nullable=False),
        sa.Column("draft_requires_approval", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workspace_settings_organization_id", "workspace_settings", ["organization_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_workspace_settings_organization_id", table_name="workspace_settings")
    op.drop_table("workspace_settings")
    op.drop_column("ai_triage_results", "reasoning")
    op.drop_column("ai_triage_results", "confidence_score")
