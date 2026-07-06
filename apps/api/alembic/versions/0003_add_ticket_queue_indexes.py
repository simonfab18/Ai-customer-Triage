"""add ticket queue indexes

Revision ID: 0003_add_ticket_queue_indexes
Revises: 0002_add_audit_logs
Create Date: 2026-07-05 00:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003_add_ticket_queue_indexes"
down_revision: str | None = "0002_add_audit_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_tickets_org_status_received_at",
        "tickets",
        ["organization_id", "status", "received_at"],
    )
    op.create_index(
        "ix_tickets_org_priority_received_at",
        "tickets",
        ["organization_id", "priority", "received_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_tickets_org_priority_received_at", table_name="tickets")
    op.drop_index("ix_tickets_org_status_received_at", table_name="tickets")