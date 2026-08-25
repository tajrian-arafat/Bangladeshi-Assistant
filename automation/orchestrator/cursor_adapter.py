"""Cursor Cloud Agents API adapter with local CLI fallback."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


CURSOR_API_BASE = os.environ.get("CURSOR_API_BASE", "https://api.cursor.com")
CURSOR_API_KEY_ENV = "CURSOR_API_KEY"


@dataclass
class CursorRunHandle:
    mode: str
    run_id: str
    agent_id: str | None = None
    cloud_run_id: str | None = None
    prompt_path: Path | None = None
    status: str = "DISPATCHED"


class CursorAdapter:
    """Adapter for Cursor Cloud Agents API v1 with local non-interactive fallback."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.api_key = os.environ.get(CURSOR_API_KEY_ENV)
        self.repo_url = os.environ.get(
            "BDA_GITHUB_REPO",
            "https://github.com/tajrian-arafat/Bangladeshi-Assistant",
        )
        self.default_branch = os.environ.get("BDA_GIT_BRANCH", "cursor/service-catalogue-discovery-3400")

    @property
    def cloud_available(self) -> bool:
        return bool(self.api_key)

    @property
    def cli_available(self) -> bool:
        return shutil.which("cursor") is not None

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("CURSOR_API_KEY not configured")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_cloud_agent(
        self,
        *,
        prompt: str,
        name: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "prompt": {"text": prompt},
            "name": name,
            "source": {
                "repository": self.repo_url,
                "ref": self.default_branch,
            },
            "metadata": metadata or {},
        }
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=60.0) as client:
            response = client.post("/v1/agents", headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    def get_cloud_run(self, agent_id: str, run_id: str) -> dict[str, Any]:
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=30.0) as client:
            response = client.get(
                f"/v1/agents/{agent_id}/runs/{run_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    def dispatch_phase(
        self,
        *,
        run_dir: Path,
        batch_id: str,
        phase: str,
        prompt: str,
        simulation: bool = False,
    ) -> CursorRunHandle:
        run_id = run_dir.name
        prompt_path = run_dir / "prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        manifest = {
            "run_id": run_id,
            "batch_id": batch_id,
            "phase": phase,
            "simulation": simulation,
            "modes_available": {
                "cloud": self.cloud_available,
                "cli": self.cli_available,
            },
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

        if simulation:
            return CursorRunHandle(mode="simulation", run_id=run_id, prompt_path=prompt_path)

        if self.cloud_available and os.environ.get("BDA_AUTOMATION_PREFER_CLOUD", "1") == "1":
            try:
                created = self.create_cloud_agent(
                    prompt=prompt,
                    name=f"bda-{batch_id}-{phase}-{run_id[:8]}",
                    metadata={"batch_id": batch_id, "phase": phase, "run_id": run_id},
                )
                agent = created.get("agent") or {}
                run = created.get("run") or {}
                handle = CursorRunHandle(
                    mode="cloud",
                    run_id=run_id,
                    agent_id=agent.get("id"),
                    cloud_run_id=run.get("id"),
                    prompt_path=prompt_path,
                )
                (run_dir / "cursor_handle.json").write_text(json.dumps(handle.__dict__, default=str, indent=2))
                return handle
            except Exception as exc:
                (run_dir / "cloud_error.log").write_text(str(exc))

        if self.cli_available and os.environ.get("BDA_AUTOMATION_USE_CLI", "0") == "1":
            # Non-interactive local fallback — writes prompt; human/agent completes result.json
            subprocess.run(
                ["cursor", "--help"],
                check=False,
                capture_output=True,
            )
            return CursorRunHandle(mode="cli", run_id=run_id, prompt_path=prompt_path)

        return CursorRunHandle(mode="local", run_id=run_id, prompt_path=prompt_path)

    def build_phase_prompt(
        self,
        *,
        template_name: str,
        batch_id: str,
        phase: str,
        context: dict[str, Any],
    ) -> str:
        template_path = self.repo_root / "automation" / "prompts" / f"{template_name}.md"
        template = template_path.read_text(encoding="utf-8") if template_path.exists() else ""
        return (
            f"# Automation Phase: {phase}\n\n"
            f"**Batch:** {batch_id}\n\n"
            f"**Mode:** LOCAL_DEV_ONLY — do NOT deploy or publish without orchestrator gates.\n\n"
            f"## Context\n\n```json\n{json.dumps(context, indent=2)}\n```\n\n"
            f"## Instructions\n\n{template}\n\n"
            f"## Required output\n\n"
            f"Write machine-readable result to:\n"
            f"`.automation/runs/<run_id>/result.json`\n\n"
            f"Follow the phase result schema exactly. Do not change workflow state directly.\n"
        )
