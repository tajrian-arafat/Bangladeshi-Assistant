"""Add Claim, ClaimEvidence, KnowledgeGap, catalogue mappings; extend SourceVersion and claim FKs.

Revision ID: 002_claims_publication
Revises: 001_initial_schema
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_claims_publication"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    op.create_table(
        "claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("research_claim_key", sa.String(length=255), nullable=True),
        sa.Column("claim_type", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=512), nullable=False),
        sa.Column("predicate", sa.String(length=256), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("structured_value", sa.JSON(), nullable=True),
        sa.Column("information_class", sa.String(length=32), nullable=False),
        sa.Column("pipeline_status", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by_admin_id", sa.Uuid(), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("supersedes_claim_id", sa.Uuid(), nullable=True),
        sa.Column("superseded_by_claim_id", sa.Uuid(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verified_by_admin_id"], ["admin_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["supersedes_claim_id"], ["claims.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["superseded_by_claim_id"], ["claims.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_claims_service_id", "claims", ["service_id"])
    op.create_index("ix_claims_research_claim_key", "claims", ["research_claim_key"])
    op.create_index("ix_claims_claim_type", "claims", ["claim_type"])
    op.create_index("ix_claims_information_class", "claims", ["information_class"])
    op.create_index("ix_claims_pipeline_status", "claims", ["pipeline_status"])

    op.create_table(
        "claim_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("source_version_id", sa.Uuid(), nullable=True),
        sa.Column("knowledge_document_id", sa.Uuid(), nullable=True),
        sa.Column("knowledge_chunk_id", sa.Uuid(), nullable=True),
        sa.Column("evidence_excerpt", sa.Text(), nullable=True),
        sa.Column("locator", sa.String(length=1024), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section", sa.String(length=512), nullable=True),
        sa.Column("selector", sa.String(length=1024), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_strength", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_version_id"], ["source_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["knowledge_document_id"], ["knowledge_documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["knowledge_chunk_id"], ["knowledge_chunks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_claim_evidence_claim_id", "claim_evidence", ["claim_id"])
    op.create_index("ix_claim_evidence_source_version_id", "claim_evidence", ["source_version_id"])

    op.create_table(
        "knowledge_gaps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=True),
        sa.Column("field_name", sa.String(length=128), nullable=True),
        sa.Column("gap_type", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("discovered_by", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("assigned_to", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_gaps_service_id", "knowledge_gaps", ["service_id"])
    op.create_index("ix_knowledge_gaps_claim_id", "knowledge_gaps", ["claim_id"])
    op.create_index("ix_knowledge_gaps_gap_type", "knowledge_gaps", ["gap_type"])
    op.create_index("ix_knowledge_gaps_status", "knowledge_gaps", ["status"])

    op.create_table(
        "service_catalogue_mappings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("catalogue_service_id", sa.String(length=128), nullable=False),
        sa.Column("runtime_service_id", sa.Uuid(), nullable=True),
        sa.Column("runtime_slug", sa.String(length=128), nullable=True),
        sa.Column("mapping_type", sa.String(length=32), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("allow_overwrite_seed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["runtime_service_id"], ["services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("catalogue_service_id", name="uq_catalogue_service_id"),
    )
    op.create_index(
        "ix_service_catalogue_mappings_catalogue_service_id",
        "service_catalogue_mappings",
        ["catalogue_service_id"],
    )
    op.create_index(
        "ix_service_catalogue_mappings_runtime_service_id",
        "service_catalogue_mappings",
        ["runtime_service_id"],
    )

    # Extend source_versions
    with op.batch_alter_table("source_versions", recreate="always" if is_sqlite else "auto") as batch:
        batch.add_column(sa.Column("canonical_url", sa.String(length=2048), nullable=True))
        batch.add_column(sa.Column("content_type", sa.String(length=128), nullable=True))
        batch.add_column(sa.Column("raw_content_path", sa.String(length=2048), nullable=True))
        batch.add_column(sa.Column("extracted_text_path", sa.String(length=2048), nullable=True))
        batch.add_column(sa.Column("title", sa.String(length=512), nullable=True))
        batch.add_column(sa.Column("language", sa.String(length=16), nullable=True))
        batch.add_column(sa.Column("http_status", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("parser_version", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("retrieval_method", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("content_length", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("fees", recreate="always" if is_sqlite else "auto") as batch:
        batch.add_column(sa.Column("claim_id", sa.Uuid(), nullable=True))
        batch.add_column(sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_foreign_key("fk_fees_claim_id", "claims", ["claim_id"], ["id"], ondelete="SET NULL")
        batch.create_index("ix_fees_claim_id", ["claim_id"])

    with op.batch_alter_table("checklist_items", recreate="always" if is_sqlite else "auto") as batch:
        batch.add_column(sa.Column("claim_id", sa.Uuid(), nullable=True))
        batch.create_foreign_key(
            "fk_checklist_items_claim_id", "claims", ["claim_id"], ["id"], ondelete="SET NULL"
        )
        batch.create_index("ix_checklist_items_claim_id", ["claim_id"])

    with op.batch_alter_table("procedure_steps", recreate="always" if is_sqlite else "auto") as batch:
        batch.add_column(sa.Column("claim_id", sa.Uuid(), nullable=True))
        batch.create_foreign_key(
            "fk_procedure_steps_claim_id", "claims", ["claim_id"], ["id"], ondelete="SET NULL"
        )
        batch.create_index("ix_procedure_steps_claim_id", ["claim_id"])


def downgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    with op.batch_alter_table("procedure_steps", recreate="always" if is_sqlite else "auto") as batch:
        batch.drop_constraint("fk_procedure_steps_claim_id", type_="foreignkey")
        batch.drop_index("ix_procedure_steps_claim_id")
        batch.drop_column("claim_id")

    with op.batch_alter_table("checklist_items", recreate="always" if is_sqlite else "auto") as batch:
        batch.drop_constraint("fk_checklist_items_claim_id", type_="foreignkey")
        batch.drop_index("ix_checklist_items_claim_id")
        batch.drop_column("claim_id")

    with op.batch_alter_table("fees", recreate="always" if is_sqlite else "auto") as batch:
        batch.drop_constraint("fk_fees_claim_id", type_="foreignkey")
        batch.drop_index("ix_fees_claim_id")
        batch.drop_column("verified_at")
        batch.drop_column("claim_id")

    with op.batch_alter_table("source_versions", recreate="always" if is_sqlite else "auto") as batch:
        for col in [
            "retrieved_at",
            "content_length",
            "retrieval_method",
            "parser_version",
            "http_status",
            "language",
            "title",
            "extracted_text_path",
            "raw_content_path",
            "content_type",
            "canonical_url",
        ]:
            batch.drop_column(col)

    op.drop_table("service_catalogue_mappings")
    op.drop_table("knowledge_gaps")
    op.drop_table("claim_evidence")
    op.drop_table("claims")
