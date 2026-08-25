"""Controlled MVP seed replacement decisions — never auto-overwrite legacy data."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.types import JSONType


class SeedReplacement(Base):
    """Explicit approval to replace legacy seed structured data with a verified claim."""

    __tablename__ = "seed_replacements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"), index=True
    )
    catalogue_service_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    replacement_kind: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)
    gate_snapshot_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    before_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rolled_back_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    service: Mapped["Service"] = relationship()  # noqa: F821
    claim: Mapped["Claim"] = relationship()  # noqa: F821
