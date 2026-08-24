"""Pipeline unit tests."""

from app.ai.pipeline.banglish import normalize_banglish
from app.ai.pipeline.intent import classify_intent
from app.ai.pipeline.language import detect_language


def test_detect_language_banglish() -> None:
    assert detect_language("passport renew korte ki lagbe") == "banglish"


def test_detect_language_bangla() -> None:
    assert detect_language("পাসপোর্ট রিনিউ") == "bn"


def test_normalize_banglish() -> None:
    result = normalize_banglish("passport renew korte ki ki lagbe")
    assert "passport" in result
    assert "renewal" in result


def test_classify_intent_documents() -> None:
    assert classify_intent("passport renew documents lagbe") == "document_list"
