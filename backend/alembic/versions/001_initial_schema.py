"""Initial schema for Bangladesh Digital Assistant."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    if not is_sqlite:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("preferred_language", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "admin_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("totp_secret", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "divisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_divisions_slug", "divisions", ["slug"])

    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )

    op.create_table(
        "model_registry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("model_type", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("path", sa.String(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "agencies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_bn", sa.String(length=512), nullable=False),
        sa.Column("name_en", sa.String(length=512), nullable=False),
        sa.Column("acronym", sa.String(length=32), nullable=True),
        sa.Column("description_bn", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(length=2048), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_agencies_slug", "agencies", ["slug"])

    op.create_table(
        "admin_user_roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("admin_user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("admin_user_id", "role_id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("admin_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=64), nullable=True),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("session_id", sa.String(length=128), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_session_id", "conversations", ["session_id"])

    op.create_table(
        "districts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("division_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("bbs_code", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_districts_slug", "districts", ["slug"])

    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("dataset_path", sa.String(length=512), nullable=True),
        sa.Column("metrics_json", sa.JSON(), nullable=True),
        sa.Column("total_queries", sa.Integer(), nullable=False),
        sa.Column("passed_queries", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("permission_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "services",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_bn", sa.String(length=512), nullable=False),
        sa.Column("name_en", sa.String(length=512), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=True),
        sa.Column("agency_id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("eligibility", sa.JSON(), nullable=True),
        sa.Column("required_documents", sa.JSON(), nullable=True),
        sa.Column("conditional_documents", sa.JSON(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("review_state", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("source_provenance", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agency_id"], ["agencies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_services_slug", "services", ["slug"])

    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("agency_id", sa.Uuid(), nullable=True),
        sa.Column("crawl_enabled", sa.Boolean(), nullable=False),
        sa.Column("requires_js", sa.Boolean(), nullable=False),
        sa.Column("rate_limit_rpm", sa.Integer(), nullable=False),
        sa.Column("schedule_cron", sa.String(length=64), nullable=True),
        sa.Column("robots_respected", sa.Boolean(), nullable=False),
        sa.Column("allow_paths", sa.JSON(), nullable=True),
        sa.Column("deny_paths", sa.JSON(), nullable=True),
        sa.Column("parser_profile", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["agency_id"], ["agencies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sources_domain", "sources", ["domain"])

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("session_token_hash", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token_hash"),
    )

    op.create_table(
        "change_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_version_id", sa.Uuid(), nullable=True),
        sa.Column("service_id", sa.Uuid(), nullable=True),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("impact", sa.String(length=16), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "checklist_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("item_type", sa.String(length=32), nullable=False),
        sa.Column("label_bn", sa.String(length=512), nullable=False),
        sa.Column("label_en", sa.String(length=512), nullable=False),
        sa.Column("description_bn", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("conditions", sa.JSON(), nullable=True),
        sa.Column("evidence_chunk_id", sa.Uuid(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "city_corporations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("district_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_city_corporations_slug", "city_corporations", ["slug"])

    op.create_table(
        "clarification_states",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "crawl_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pages_discovered", sa.Integer(), nullable=False),
        sa.Column("pages_fetched", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "fees",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("label_bn", sa.String(length=512), nullable=False),
        sa.Column("label_en", sa.String(length=512), nullable=False),
        sa.Column("amount", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("evidence_chunk_id", sa.Uuid(), nullable=True),
        sa.Column("notes_bn", sa.Text(), nullable=True),
        sa.Column("notes_en", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "forms",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("form_code", sa.String(length=64), nullable=True),
        sa.Column("name_bn", sa.String(length=512), nullable=False),
        sa.Column("name_en", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "geography_aliases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("alias_type", sa.String(length=32), nullable=False),
        sa.Column("division_id", sa.Uuid(), nullable=True),
        sa.Column("district_id", sa.Uuid(), nullable=True),
        sa.Column("upazila_id", sa.Uuid(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias", "alias_type"),
    )
    op.create_index("ix_geography_aliases_alias", "geography_aliases", ["alias"])

    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("confidence", sa.String(length=16), nullable=True),
        sa.Column("intent", sa.String(length=64), nullable=True),
        sa.Column("service_slug", sa.String(length=128), nullable=True),
        sa.Column("answer_json", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("processing_ms", sa.Integer(), nullable=True),
        sa.Column("llm_used", sa.Boolean(), nullable=False),
        sa.Column("fallback_mode", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "municipalities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("district_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_municipalities_slug", "municipalities", ["slug"])

    op.create_table(
        "procedures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("title_bn", sa.String(length=512), nullable=False),
        sa.Column("title_en", sa.String(length=512), nullable=False),
        sa.Column("description_bn", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("preconditions", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "review_queue_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("change_event_id", sa.Uuid(), nullable=True),
        sa.Column("service_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assigned_to"], ["admin_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["change_event_id"], ["change_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "service_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("link_type", sa.String(length=32), nullable=False),
        sa.Column("label_bn", sa.String(length=512), nullable=False),
        sa.Column("label_en", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_id", "url"),
    )

    op.create_table(
        "service_offices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("agency_id", sa.Uuid(), nullable=True),
        sa.Column("district_id", sa.Uuid(), nullable=True),
        sa.Column("name_bn", sa.String(length=512), nullable=False),
        sa.Column("name_en", sa.String(length=512), nullable=False),
        sa.Column("address_bn", sa.Text(), nullable=True),
        sa.Column("address_en", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["agency_id"], ["agencies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "source_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "upazilas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("district_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("bbs_code", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_upazilas_slug", "upazilas", ["slug"])

    op.create_table(
        "checklist_conditions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("checklist_item_id", sa.Uuid(), nullable=False),
        sa.Column("condition_key", sa.String(length=128), nullable=False),
        sa.Column("condition_value", sa.Text(), nullable=True),
        sa.Column("operator", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["checklist_item_id"], ["checklist_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "crawl_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("crawl_job_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["crawl_job_id"], ["crawl_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("message_id", sa.Uuid(), nullable=True),
        sa.Column("service_id", sa.Uuid(), nullable=True),
        sa.Column("feedback_type", sa.String(length=64), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_version_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("untrusted_content", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["source_version_id"], ["source_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "message_feedback",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("feedback_type", sa.String(length=64), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "procedure_steps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("procedure_id", sa.Uuid(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("title_bn", sa.String(length=512), nullable=False),
        sa.Column("title_en", sa.String(length=512), nullable=False),
        sa.Column("description_bn", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("preconditions", sa.JSON(), nullable=True),
        sa.Column("required_document_ids", sa.JSON(), nullable=True),
        sa.Column("fee_ids", sa.JSON(), nullable=True),
        sa.Column("official_url", sa.String(length=2048), nullable=True),
        sa.Column("responsible_agency_id", sa.Uuid(), nullable=True),
        sa.Column("location_hint", sa.String(length=512), nullable=True),
        sa.Column("estimated_duration", sa.String(length=128), nullable=True),
        sa.Column("dependencies", sa.JSON(), nullable=True),
        sa.Column("conditions", sa.JSON(), nullable=True),
        sa.Column("evidence_ids", sa.JSON(), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["procedure_id"], ["procedures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["responsible_agency_id"], ["agencies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "unions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("upazila_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["upazila_id"], ["upazilas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_unions_slug", "unions", ["slug"])

    op.create_table(
        "wards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("city_corporation_id", sa.Uuid(), nullable=False),
        sa.Column("ward_number", sa.Integer(), nullable=False),
        sa.Column("name_bn", sa.String(length=255), nullable=True),
        sa.Column("name_en", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["city_corporation_id"], ["city_corporations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    embedding_type = sa.Text() if is_sqlite else sa.dialects.postgresql.ARRAY(sa.Float())
    if not is_sqlite:
        try:
            from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]

            embedding_type = Vector(1024)
        except ImportError:
            embedding_type = sa.JSON()

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("service_id", sa.Uuid(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("embedding", embedding_type, nullable=True),
        sa.Column("search_vector", sa.Text(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["knowledge_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "message_citations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("knowledge_chunk_id", sa.Uuid(), nullable=True),
        sa.Column("source_version_id", sa.Uuid(), nullable=True),
        sa.Column("evidence_id", sa.String(length=64), nullable=True),
        sa.Column("source_title", sa.String(length=512), nullable=True),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("tier", sa.Integer(), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_chunk_id"], ["knowledge_chunks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_version_id"], ["source_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    tables = [
        "message_citations",
        "knowledge_chunks",
        "wards",
        "unions",
        "procedure_steps",
        "message_feedback",
        "knowledge_documents",
        "feedback",
        "crawl_attempts",
        "checklist_conditions",
        "upazilas",
        "source_versions",
        "service_offices",
        "service_links",
        "review_queue_items",
        "procedures",
        "municipalities",
        "messages",
        "geography_aliases",
        "forms",
        "fees",
        "crawl_jobs",
        "clarification_states",
        "city_corporations",
        "checklist_items",
        "change_events",
        "user_sessions",
        "sources",
        "services",
        "role_permissions",
        "refresh_tokens",
        "evaluation_runs",
        "districts",
        "conversations",
        "audit_logs",
        "admin_user_roles",
        "agencies",
        "model_registry",
        "feature_flags",
        "divisions",
        "admin_users",
        "permissions",
        "roles",
        "users",
    ]
    for table in tables:
        op.drop_table(table)
