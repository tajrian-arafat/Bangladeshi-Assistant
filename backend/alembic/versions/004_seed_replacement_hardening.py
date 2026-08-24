"""Add seed_replacements table for controlled MVP seed overwrite.

Revision ID: 004_seed_replacement_hardening
Revises: 003_catalogue_runtime_sync
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_seed_replacement_hardening"
down_revision: Union[str, None] = "003_catalogue_runtime_sync"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "seed_replacements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("catalogue_service_id", sa.String(length=128), nullable=True),
        sa.Column("batch_id", sa.String(length=64), nullable=True),
        sa.Column("replacement_kind", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("gate_snapshot_json", sa.JSON(), nullable=True),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rolled_back_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_seed_replacements_service_id", "seed_replacements", ["service_id"])
    op.create_index("ix_seed_replacements_claim_id", "seed_replacements", ["claim_id"])
    op.create_index("ix_seed_replacements_status", "seed_replacements", ["status"])
    op.create_index(
        "ix_seed_replacements_replacement_kind", "seed_replacements", ["replacement_kind"]
    )


def downgrade() -> None:
    op.drop_index("ix_seed_replacements_replacement_kind", table_name="seed_replacements")
    op.drop_index("ix_seed_replacements_status", table_name="seed_replacements")
    op.drop_index("ix_seed_replacements_claim_id", table_name="seed_replacements")
    op.drop_index("ix_seed_replacements_service_id", table_name="seed_replacements")
    op.drop_table("seed_replacements")
