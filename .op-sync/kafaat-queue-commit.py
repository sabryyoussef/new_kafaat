#!/usr/bin/env python3
"""Queue current git HEAD for OpenProject sync (runs on Kafaat server)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> int:
    repo = Path(git("rev-parse", "--show-toplevel"))
    sha = git("rev-parse", "HEAD")
    queue_dir = repo / ".op-sync" / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    out_file = queue_dir / f"{sha}.json"
    if out_file.exists():
        return 0
    files = subprocess.check_output(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
        text=True,
    ).strip().splitlines()
    remote = ""
    try:
        remote = git("remote", "get-url", "origin")
    except subprocess.CalledProcessError:
        pass
    payload = {
        "server": "kafaat",
        "project_id": 10,
        "parent_wp_id": 87,
        "parent_subject": "edafa_kafaat_parent",
        "commit": {
            "sha": sha,
            "subject": git("log", "-1", "--pretty=%s", sha),
            "author": git("log", "-1", "--pretty=format:%an <%ae>", sha),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "files": "\n".join(files),
            "remote": remote,
        },
    }
    out_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[op-sync] queued commit {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
