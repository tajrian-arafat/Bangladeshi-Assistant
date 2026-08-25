"""Safety policy validation."""

from __future__ import annotations

FORBIDDEN_PATTERNS = [
    "submit application on your behalf",
    "your password",
    "your otp",
    "your pin",
    "payment completed",
]


def validate_safety(text: str) -> None:
    lowered = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in lowered:
            raise ValueError(f"Unsafe response blocked: contains '{pattern}'")
