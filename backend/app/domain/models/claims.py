"""Claim, ClaimEvidence, KnowledgeGap, and catalogue↔runtime mapping models."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.types import JSONType


class Claim(Base):
    """Atomic factual assertion about a service. Not publishable until VERIFIED."""

    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True
    )
    research_claim_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    claim_type: Mapped[str] = mapped_column(String(64), index=True)
    subject: Mapped[str] = mapped_column(String(512))
    predicate: Mapped[str] = mapped_column(String(256))
    value: Mapped[str] = mapped_column(Text)
    structured_value: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    information_class: Mapped[str] = mapped_column(String(32), default="DISCOVERY", index=True)
    pipeline_status: Mapped[str] = mapped_column(
        String(32), default="DISCOVERED", index=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    supersedes_claim_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True
    )
    superseded_by_claim_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    service: Mapped["Service"] = relationship(  # noqa: F821
        back_populates="claims"
    )
    evidence_links: Mapped[list["ClaimEvidence"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    gaps: Mapped[list["KnowledgeGap"]] = relationship(back_populates="claim")


class ClaimEvidence(Base):
    """Evidence link for a claim. Trace: Claim → Evidence → SourceVersion → Source."""

    __tablename__ = "claim_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"), index=True
    )
    source_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_versions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    knowledge_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="SET NULL"), nullable=True
    )
    knowledge_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("knowledge_chunks.id", ondelete="SET NULL"), nullable=True
    )
    evidence_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    locator: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(512), nullable=True)
    selector: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    evidence_strength: Mapped[str] = mapped_column(String(32), default="WEAK")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    claim: Mapped["Claim"] = relationship(back_populates="evidence_links")
    source_version: Mapped["SourceVersion | None"] = relationship(  # noqa: F821
        back_populates="claim_evidence_links"
    )


class KnowledgeGap(Base):
    """Tracked missing or conflicting knowledge for a service/claim."""

    __tablename__ = "knowledge_gaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True
    )
    claim_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True
    )
    field_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    gap_type: Mapped[str] = mapped_column(String(64), index=True)
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM")
    description: Mapped[str] = mapped_column(Text)
    discovered_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="OPEN", index=True)
    assigned_to: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    service: Mapped["Service"] = relationship(back_populates="knowledge_gaps")  # noqa: F821
    claim: Mapped["Claim | None"] = relationship(back_populates="gaps")


class ServiceCatalogueMapping(Base):
    """Explicit catalogue_service_id ↔ runtime Service mapping. No silent overwrite."""

    __tablename__ = "service_catalogue_mappings"
    __table_args__ = (
        UniqueConstraint("catalogue_service_id", name="uq_catalogue_service_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    catalogue_service_id: Mapped[str] = mapped_column(String(128), index=True)
    runtime_service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    runtime_slug: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mapping_type: Mapped[str] = mapped_column(String(32))
    mapping_status: Mapped[str] = mapped_column(
        String(32), default="UNRESOLVED", index=True
    )
    review_status: Mapped[str] = mapped_column(String(32), default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    allow_overwrite_seed: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    runtime_service: Mapped["Service | None"] = relationship(  # noqa: F821
        back_populates="catalogue_mappings"
    )
