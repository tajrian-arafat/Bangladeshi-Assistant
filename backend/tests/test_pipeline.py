"""Pipeline unit tests."""

from app.ai.pipeline.banglish import normalize_banglish
from app.ai.pipeline.intent import classify_intent
from app.ai.pipeline.language import detect_language


def test_detect_language_banglish() -> None:
    assert detect_language("passport renew korte ki lagbe") == "banglish"


def test_detect_language_bangla() -> None:
    assert detect_language("পাসপোর্ট রিনিউ") == "bn"


def test_normalize_banglish() -> None:
    result = normalize_banglish("passport renew korte ki ki lage")
    assert "passport" in result
    assert "renewal" in result


def test_normalize_banglish_jonmo() -> None:
    result = normalize_banglish("jonmo nibondhon korte ki ki lage?")
    assert "birth" in result
    assert "registration" in result


def test_classify_intent_documents() -> None:
    assert classify_intent("passport renew documents lagbe") == "document_list"


def test_classify_intent_bangla_documents() -> None:
    assert classify_intent("জন্ম নিবন্ধন করতে কী কী লাগে?") == "document_list"


def test_classify_intent_fee() -> None:
    assert classify_intent("NID correction fee koto?") == "fee_inquiry"
