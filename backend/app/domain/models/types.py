"""Custom SQLAlchemy column types."""

import json
from typing import Any

from sqlalchemy import Text, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.core.config import get_settings


class EmbeddingType(TypeDecorator[list[float] | None]):
    """Store embeddings as pgvector on PostgreSQL or JSON text on SQLite."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]

                return dialect.type_descriptor(Vector(1024))
            except ImportError:
                return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(Text())

    def process_bind_param(
        self, value: list[float] | None, dialect: Any
    ) -> list[float] | str | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(
        self, value: list[float] | str | None, dialect: Any
    ) -> list[float] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            if isinstance(value, str):
                return json.loads(value)
            return list(value)
        if isinstance(value, str):
            return json.loads(value)
        return list(value)


class JSONType(TypeDecorator[dict[str, Any] | list[Any] | None]):
    """JSON column that uses JSONB on PostgreSQL and JSON on SQLite."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
