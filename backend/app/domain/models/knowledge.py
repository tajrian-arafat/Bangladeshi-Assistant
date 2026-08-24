"""Knowledge core models: agencies, services, sources, documents."""

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
from app.domain.models.types import EmbeddingType, JSONType


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name_bn: Mapped[str] = mapped_column(String(512))
    name_en: Mapped[str] = mapped_column(String(512))
    acronym: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    services: Mapped[list["Service"]] = relationship(back_populates="agency")
    sources: Mapped[list["Source"]] = relationship(back_populates="agency")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name_bn: Mapped[str] = mapped_column(String(512))
    name_en: Mapped[str] = mapped_column(String(512))
    aliases: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    agency_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agencies.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="UNDER_REVIEW")
    eligibility: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    required_documents: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    conditional_documents: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_state: Mapped[str] = mapped_column(String(32), default="DRAFT")
    version: Mapped[int] = mapped_column(Integer, default=1)
    source_provenance: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    agency: Mapped["Agency"] = relationship(back_populates="services")
    procedures: Mapped[list["Procedure"]] = relationship(back_populates="service")
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(back_populates="service")
    fees: Mapped[list["Fee"]] = relationship(back_populates="service")
    forms: Mapped[list["Form"]] = relationship(back_populates="service")
    service_links: Mapped[list["ServiceLink"]] = relationship(back_populates="service")
    service_offices: Mapped[list["ServiceOffice"]] = relationship(back_populates="service")
    knowledge_chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="service")
    claims: Mapped[list["Claim"]] = relationship(back_populates="service")  # noqa: F821
    knowledge_gaps: Mapped[list["KnowledgeGap"]] = relationship(  # noqa: F821
        back_populates="service"
    )
    catalogue_mappings: Mapped[list["ServiceCatalogueMapping"]] = relationship(  # noqa: F821
        back_populates="runtime_service"
    )


class Procedure(Base):
    __tablename__ = "procedures"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    key: Mapped[str] = mapped_column(String(128))
    title_bn: Mapped[str] = mapped_column(String(512))
    title_en: Mapped[str] = mapped_column(String(512))
    description_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    preconditions: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    service: Mapped["Service"] = relationship(back_populates="procedures")
    steps: Mapped[list["ProcedureStep"]] = relationship(back_populates="procedure")


class ProcedureStep(Base):
    __tablename__ = "procedure_steps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procedures.id", ondelete="CASCADE")
    )
    order: Mapped[int] = mapped_column(Integer)
    key: Mapped[str] = mapped_column(String(128))
    title_bn: Mapped[str] = mapped_column(String(512))
    title_en: Mapped[str] = mapped_column(String(512))
    description_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    preconditions: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    required_document_ids: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    fee_ids: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    official_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    responsible_agency_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agencies.id", ondelete="SET NULL"), nullable=True
    )
    location_hint: Mapped[str | None] = mapped_column(String(512), nullable=True)
    estimated_duration: Mapped[str | None] = mapped_column(String(128), nullable=True)
    dependencies: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    conditions: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    evidence_ids: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    claim_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    procedure: Mapped["Procedure"] = relationship(back_populates="steps")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer, default=0)
    item_type: Mapped[str] = mapped_column(String(32))
    label_bn: Mapped[str] = mapped_column(String(512))
    label_en: Mapped[str] = mapped_column(String(512))
    description_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    evidence_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("knowledge_chunks.id", ondelete="SET NULL"), nullable=True
    )
    claim_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped["Service"] = relationship(back_populates="checklist_items")
    checklist_conditions: Mapped[list["ChecklistCondition"]] = relationship(
        back_populates="checklist_item"
    )


class ChecklistCondition(Base):
    __tablename__ = "checklist_conditions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    checklist_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("checklist_items.id", ondelete="CASCADE")
    )
    condition_key: Mapped[str] = mapped_column(String(128))
    condition_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    operator: Mapped[str] = mapped_column(String(32), default="eq")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    checklist_item: Mapped["ChecklistItem"] = relationship(back_populates="checklist_conditions")


class Fee(Base):
    __tablename__ = "fees"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    label_bn: Mapped[str] = mapped_column(String(512))
    label_en: Mapped[str] = mapped_column(String(512))
    amount: Mapped[str] = mapped_column(String(64))
    currency: Mapped[str] = mapped_column(String(8), default="BDT")
    version: Mapped[int] = mapped_column(Integer, default=1)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    evidence_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("knowledge_chunks.id", ondelete="SET NULL"), nullable=True
    )
    claim_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped["Service"] = relationship(back_populates="fees")


class Form(Base):
    __tablename__ = "forms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    form_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name_bn: Mapped[str] = mapped_column(String(512))
    name_en: Mapped[str] = mapped_column(String(512))
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped["Service"] = relationship(back_populates="forms")


class ServiceLink(Base):
    __tablename__ = "service_links"
    __table_args__ = (UniqueConstraint("service_id", "url"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    link_type: Mapped[str] = mapped_column(String(32))
    label_bn: Mapped[str] = mapped_column(String(512))
    label_en: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(2048))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped["Service"] = relationship(back_populates="service_links")


class ServiceOffice(Base):
    __tablename__ = "service_offices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agencies.id", ondelete="SET NULL"), nullable=True
    )
    district_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("districts.id", ondelete="SET NULL"), nullable=True
    )
    name_bn: Mapped[str] = mapped_column(String(512))
    name_en: Mapped[str] = mapped_column(String(512))
    address_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped["Service"] = relationship(back_populates="service_offices")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tier: Mapped[int] = mapped_column(Integer, default=1)
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agencies.id", ondelete="SET NULL"), nullable=True
    )
    crawl_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_js: Mapped[bool] = mapped_column(Boolean, default=False)
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=10)
    schedule_cron: Mapped[str | None] = mapped_column(String(64), nullable=True)
    robots_respected: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_paths: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    deny_paths: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    parser_profile: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    agency: Mapped["Agency | None"] = relationship(back_populates="sources")
    versions: Mapped[list["SourceVersion"]] = relationship(back_populates="source")


class SourceVersion(Base):
    """Durable snapshot reference for a source URL at retrieval time.

    Large bodies live on filesystem/object storage via raw_content_path /
    extracted_text_path — not inline in relational columns.
    """

    __tablename__ = "source_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(2048))
    canonical_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    raw_content_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    extracted_text_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    retrieval_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["Source"] = relationship(back_populates="versions")
    documents: Mapped[list["KnowledgeDocument"]] = relationship(back_populates="source_version")
    claim_evidence_links: Mapped[list["ClaimEvidence"]] = relationship(  # noqa: F821
        back_populates="source_version"
    )


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_versions.id", ondelete="CASCADE")
    )
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="bn")
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    untrusted_content: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source_version: Mapped["SourceVersion"] = relationship(back_populates="documents")
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="document")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE")
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(16), default="bn")
    embedding: Mapped[list[float] | None] = mapped_column(EmbeddingType, nullable=True)
    search_vector: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")
    service: Mapped["Service | None"] = relationship(back_populates="knowledge_chunks")
