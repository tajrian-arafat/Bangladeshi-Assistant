"""Optional local LLM adapter with deterministic fallback."""

from __future__ import annotations

import httpx

from app.core.config import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return self.settings.feature_llm_enabled

    async def summarize(self, evidence_json: str, user_message: str, language: str) -> str | None:
        if not self.enabled:
            return None
        try:
            async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                    json={
                        "model": self.settings.llm_model_primary,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a Bangladesh government service assistant. "
                                    "Use ONLY the provided evidence JSON. "
                                    "If a fact is missing, say you do not know. "
                                    "Never invent URLs, fees, or documents."
                                ),
                            },
                            {
                                "role": "user",
                                "content": f"Evidence:\n{evidence_json}\n\nQuestion:\n{user_message}",
                            },
                        ],
                        "temperature": 0.1,
                        "max_tokens": self.settings.llm_max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None
