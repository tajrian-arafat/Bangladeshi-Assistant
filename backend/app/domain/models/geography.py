"""Geography models for Bangladesh administrative divisions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Division(Base):
    __tablename__ = "divisions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_bn: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    districts: Mapped[list["District"]] = relationship(back_populates="division")


class District(Base):
    __tablename__ = "districts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    division_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("divisions.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_bn: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str] = mapped_column(String(255))
    bbs_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    division: Mapped["Division"] = relationship(back_populates="districts")
    upazilas: Mapped[list["Upazila"]] = relationship(back_populates="district")


class Upazila(Base):
    __tablename__ = "upazilas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(128), index=True)
    name_bn: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str] = mapped_column(String(255))
    bbs_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    district: Mapped["District"] = relationship(back_populates="upazilas")
    unions: Mapped[list["Union"]] = relationship(back_populates="upazila")


class Union(Base):
    __tablename__ = "unions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    upazila_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("upazilas.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(128), index=True)
    name_bn: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    upazila: Mapped["Upazila"] = relationship(back_populates="unions")


class Municipality(Base):
    __tablename__ = "municipalities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(128), index=True)
    name_bn: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CityCorporation(Base):
    __tablename__ = "city_corporations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name_bn: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    wards: Mapped[list["Ward"]] = relationship(back_populates="city_corporation")


class Ward(Base):
    __tablename__ = "wards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    city_corporation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("city_corporations.id", ondelete="CASCADE")
    )
    ward_number: Mapped[int] = mapped_column()
    name_bn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    city_corporation: Mapped["CityCorporation"] = relationship(back_populates="wards")


class GeographyAlias(Base):
    __tablename__ = "geography_aliases"
    __table_args__ = (UniqueConstraint("alias", "alias_type"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    alias: Mapped[str] = mapped_column(String(255), index=True)
    alias_type: Mapped[str] = mapped_column(String(32))
    division_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("divisions.id", ondelete="CASCADE"), nullable=True
    )
    district_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("districts.id", ondelete="CASCADE"), nullable=True
    )
    upazila_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("upazilas.id", ondelete="CASCADE"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
