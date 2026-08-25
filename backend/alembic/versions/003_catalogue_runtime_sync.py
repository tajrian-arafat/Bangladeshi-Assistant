"""Add catalogue_service_id on services and mapping_status/provenance on mappings.

Revision ID: 003_catalogue_runtime_sync
Revises: 002_claims_publication
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_catalogue_runtime_sync"
down_revision: Union[str, None] = "002_claims_publication"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    with op.batch_alter_table("services", recreate="always" if is_sqlite else "auto") as batch:
        batch.add_column(sa.Column("catalogue_service_id", sa.String(length=128), nullable=True))
        batch.create_index("ix_services_catalogue_service_id", ["catalogue_service_id"], unique=True)

    with op.batch_alter_table(
        "service_catalogue_mappings", recreate="always" if is_sqlite else "auto"
    ) as batch:
        batch.add_column(
            sa.Column(
                "mapping_status",
                sa.String(length=32),
                nullable=False,
                server_default="UNRESOLVED",
            )
        )
        batch.add_column(sa.Column("provenance_json", sa.JSON(), nullable=True))
        batch.create_index("ix_service_catalogue_mappings_mapping_status", ["mapping_status"])


def downgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    with op.batch_alter_table(
        "service_catalogue_mappings", recreate="always" if is_sqlite else "auto"
    ) as batch:
        batch.drop_index("ix_service_catalogue_mappings_mapping_status")
        batch.drop_column("provenance_json")
        batch.drop_column("mapping_status")

    with op.batch_alter_table("services", recreate="always" if is_sqlite else "auto") as batch:
        batch.drop_index("ix_services_catalogue_service_id")
        batch.drop_column("catalogue_service_id")
