"""GitHub status inspection — read-only helpers."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitStatus:
    branch: str
    clean: bool
    modified: list[str]
    untracked: list[str]
    ahead: int
    behind: int


class GitHubAdapter:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )

    def current_branch(self) -> str:
        result = self._run("branch", "--show-current")
        return (result.stdout or "").strip() or "unknown"

    def status(self) -> GitStatus:
        branch = self.current_branch()
        porcelain = self._run("status", "--porcelain")
        modified: list[str] = []
        untracked: list[str] = []
        for line in (porcelain.stdout or "").splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if line.startswith("??"):
                untracked.append(path)
            else:
                modified.append(path)
        upstream = self._run("rev-list", "--left-right", "--count", f"origin/{branch}...HEAD")
        ahead, behind = 0, 0
        if upstream.returncode == 0 and upstream.stdout:
            parts = upstream.stdout.strip().split()
            if len(parts) == 2:
                behind, ahead = int(parts[0]), int(parts[1])
        return GitStatus(
            branch=branch,
            clean=not modified and not untracked,
            modified=modified,
            untracked=untracked,
            ahead=ahead,
            behind=behind,
        )

    def snapshot(self) -> dict:
        st = self.status()
        return {
            "branch": st.branch,
            "clean": st.clean,
            "modified_count": len(st.modified),
            "untracked_count": len(st.untracked),
            "ahead": st.ahead,
            "behind": st.behind,
        }

    def write_snapshot(self, run_dir: Path) -> Path:
        path = run_dir / "git_snapshot.json"
        path.write_text(json.dumps(self.snapshot(), indent=2) + "\n")
        return path
