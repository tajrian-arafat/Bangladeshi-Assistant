"""Intent classification — re-exports routing module for backward compatibility."""

from __future__ import annotations

from app.ai.routing.intent_classifier import classify_intent, classify_intents

__all__ = ["classify_intent", "classify_intents"]
