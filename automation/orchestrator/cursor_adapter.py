"""Cursor Cloud Agents API adapter with local CLI fallback."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, asdict
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
    """Adapter for Cursor Cloud Agents API v1 with in-process cloud fallback."""

    TERMINAL_RUN_STATUSES = frozenset({"COMPLETED", "FINISHED", "SUCCEEDED", "SUCCESS", "FAILED", "CANCELLED", "ERROR"})

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.api_key = os.environ.get(CURSOR_API_KEY_ENV)
        self.repo_url = os.environ.get(
            "BDA_GITHUB_REPO",
            "https://github.com/tajrian-arafat/Bangladeshi-Assistant",
        )
        self.default_branch = os.environ.get(
            "BDA_GIT_BRANCH",
            os.environ.get("GIT_BRANCH", "cursor/batch-03c-brta-fitness-tax-permit-3400"),
        )

    @property
    def cloud_available(self) -> bool:
        return bool(self.api_key)

    @property
    def in_process_cloud(self) -> bool:
        return os.environ.get("CURSOR_AGENT") == "1" and bool(os.environ.get("CURSOR_CONVERSATION_ID"))

    @property
    def cli_available(self) -> bool:
        return shutil.which("cursor") is not None

    def _auth(self) -> tuple[str, str]:
        if not self.api_key:
            raise RuntimeError("CURSOR_API_KEY not configured")
        return (self.api_key, "")

    def _headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def create_cloud_agent(
        self,
        *,
        prompt: str,
        name: str,
        metadata: dict[str, str] | None = None,
        starting_ref: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "prompt": {"text": prompt},
            "name": name[:100],
            "repos": [
                {
                    "url": self.repo_url if self.repo_url.startswith("http") else f"https://{self.repo_url}",
                    "startingRef": starting_ref or self.default_branch,
                }
            ],
            "autoCreatePR": False,
            "mode": "agent",
        }
        if metadata:
            payload["metadata"] = metadata
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=60.0) as client:
            response = client.post("/v1/agents", auth=self._auth(), headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    def continue_run(self, agent_id: str, prompt: str) -> dict[str, Any]:
        payload = {"prompt": {"text": prompt}, "mode": "agent"}
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=60.0) as client:
            response = client.post(
                f"/v1/agents/{agent_id}/runs",
                auth=self._auth(),
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def get_cloud_agent(self, agent_id: str) -> dict[str, Any]:
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=30.0) as client:
            response = client.get(f"/v1/agents/{agent_id}", auth=self._auth(), headers=self._headers())
            response.raise_for_status()
            return response.json()

    def get_cloud_run(self, agent_id: str, run_id: str) -> dict[str, Any]:
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=30.0) as client:
            response = client.get(
                f"/v1/agents/{agent_id}/runs/{run_id}",
                auth=self._auth(),
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    def cancel_run(self, agent_id: str, run_id: str) -> dict[str, Any]:
        with httpx.Client(base_url=CURSOR_API_BASE, timeout=30.0) as client:
            response = client.post(
                f"/v1/agents/{agent_id}/runs/{run_id}/cancel",
                auth=self._auth(),
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    def wait_for_completion(
        self,
        agent_id: str,
        run_id: str,
        *,
        poll_interval: float = 10.0,
        timeout_sec: float = 3600.0,
    ) -> dict[str, Any]:
        deadline = time.time() + timeout_sec
        last: dict[str, Any] = {}
        while time.time() < deadline:
            last = self.get_cloud_run(agent_id, run_id)
            run = last.get("run") or last
            status = (run.get("status") or "").upper()
            if status in self.TERMINAL_RUN_STATUSES:
                return last
            time.sleep(poll_interval)
        raise TimeoutError(f"Cloud run {run_id} did not complete within {timeout_sec}s")

    def verify_api(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "CURSOR_API_KEY not set"
        try:
            with httpx.Client(base_url=CURSOR_API_BASE, timeout=15.0) as client:
                response = client.get("/v1/me", auth=self._auth(), headers=self._headers())
                if response.status_code == 200:
                    return True, "ok"
                return False, response.text[:200]
        except Exception as exc:
            return False, str(exc)

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
                "cloud_api": self.cloud_available,
                "in_process_cloud": self.in_process_cloud,
                "cli": self.cli_available,
            },
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

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
                (run_dir / "cursor_handle.json").write_text(
                    json.dumps({k: str(v) if isinstance(v, Path) else v for k, v in asdict(handle).items()}, indent=2)
                    + "\n",
                    encoding="utf-8",
                )
                return handle
            except Exception as exc:
                (run_dir / "cloud_error.log").write_text(str(exc), encoding="utf-8")

        if self.in_process_cloud:
            return CursorRunHandle(
                mode="in_process_cloud",
                run_id=run_id,
                agent_id=os.environ.get("CURSOR_CONVERSATION_ID"),
                prompt_path=prompt_path,
            )

        if self.cli_available and os.environ.get("BDA_AUTOMATION_USE_CLI", "0") == "1":
            subprocess.run(["cursor", "--help"], check=False, capture_output=True)
            return CursorRunHandle(mode="cli", run_id=run_id, prompt_path=prompt_path)

        return CursorRunHandle(mode="unavailable", run_id=run_id, prompt_path=prompt_path)

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
