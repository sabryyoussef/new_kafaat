#!/usr/bin/env python3
"""
Create OpenProject WP: Kafaat UAT notes client reply (proof + Playwright).

Parent: #87  | Project: 10  | Relates: #351–#358

  set -a; source /root/.config/openproject/env; set +a
  export OP_API_KEY="$OPENPROJECT_API_TOKEN"   # or paste a fresh token
  python3 docs/op_meeting_nabil/uat_client_reply_wp/create_op_wp.py
"""
from __future__ import annotations

import base64
import json
import os
import socket as _socket
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

_FUNNEL_IP = "176.58.90.145"
_OP_HOSTS = {"master.tailcf9988.ts.net", "master.talkf9988.ts.net"}
_orig_getaddrinfo = _socket.getaddrinfo


def _getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host in _OP_HOSTS:
        return _orig_getaddrinfo(_FUNNEL_IP, port, _socket.AF_INET, type, proto, flags)
    return _orig_getaddrinfo(host, port, family, type, proto, flags)


_socket.getaddrinfo = _getaddrinfo

OUT_DIR = Path(__file__).resolve().parent
REPO_DOCS = OUT_DIR.parent

OP_URL = (
    os.environ.get("OP_URL")
    or os.environ.get("OPENPROJECT_BASE_URL")
    or "https://projects.drpaws.ai"
).rstrip("/")
OP_UI_URL = (
    os.environ.get("OP_UI_URL")
    or os.environ.get("OPENPROJECT_UI_URL")
    or OP_URL
).rstrip("/")
OP_API_KEY = (
    os.environ.get("OP_API_KEY")
    or os.environ.get("OPENPROJECT_API_TOKEN")
    or ""
).strip()
OP_USER = os.environ.get("OP_USER", "apikey")
PROJECT_ID = int(os.environ.get("OP_PROJECT_ID") or os.environ.get("OPENPROJECT_PROJECT_ID") or "10")
PARENT_WP_ID = int(os.environ.get("OP_PARENT_WP_ID") or os.environ.get("OPENPROJECT_PARENT_WP_ID") or "87")
RELATED = [351, 352, 353, 354, 355, 356, 357, 358]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

SUBJECT = (
    "[Kafaat] UAT notes client reply — detailed proof + Playwright screenshots (8 items)"
)

DESCRIPTION = """## Purpose

Delivery work package to **reply in detail** to the client Kafaat UAT notes (8 items), with **proof**, **Playwright tests**, and **screenshots**.

Source: Arabic tester feedback covering the same scope as meeting WPs #351–#358.

### Client items

1. Search students by national ID — claimed Done
2. Student status (accepted / rejected / under review / cancelled)
3. Voucher number on student screen
4. Explain offline Batch mechanism
5. Excel assign trainees to sales
6. Courses/programs not showing after create
7. Arabic UI translation
8. Batch attendance QR for enrolled students

## Deliverables

- [ ] Detailed Arabic (+ EN) reply for **each** of the 8 questions
- [ ] Proof per item (field/menu/module version, DB evidence)
- [ ] Playwright suite with screenshots for UI-verifiable items
- [ ] Evidence pack: `docs/op_meeting_nabil/uat_client_reply_wp/`
- [ ] Odoo mirror task with attachments
- [ ] WhatsApp / client-ready summary

## Related

- Parent: #87 `edafa_kafaat_parent`
- Meeting WPs: #351–#358
- Verification draft: `docs/op_meeting_nabil/analysis/KAFAAT_UAT_NOTES_VERIFICATION_REPORT.md`

## Acceptance

- [ ] Client can open this WP and see item-by-item answers with screenshots
- [ ] Playwright green on `sabry-test` for covered items
- [ ] Clear next actions for open items (#6 ops, #7 S4, #8 TR_K19 session+QR smoke)
"""


def _ssl_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def api_at(base: str, method: str, path: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode()
    auth = base64.b64encode(f"{OP_USER}:{OP_API_KEY}".encode()).decode()
    req = urllib.request.Request(
        f"{base}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45, context=_ssl_ctx()) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} {path}: {err[:800]}") from e


def main() -> int:
    if not OP_API_KEY:
        print(
            "ERROR: Set OP_API_KEY or OPENPROJECT_API_TOKEN "
            "(OpenProject → Avatar → Access tokens → API).",
            file=sys.stderr,
        )
        return 1

    bases = []
    for b in (
        OP_URL,
        "https://projects.drpaws.ai",
        "https://master.tailcf9988.ts.net",
    ):
        if b and b not in bases:
            bases.append(b)

    last_err = None
    base_url = None
    root = None
    for base in bases:
        try:
            st, root = api_at(base, "GET", "/api/v3")
            base_url = base
            print(f"OpenProject OK ({st}) @ {base_url}: {root.get('instanceName')}")
            break
        except SystemExit as e:
            last_err = e
            print(f"  skip {base}: {e}")
    if root is None or base_url is None:
        print(f"ERROR: API auth failed on all bases.\n{last_err}", file=sys.stderr)
        return 2

    if "projects.drpaws.ai" in base_url:
        ui_url = base_url
    else:
        ui_url = os.environ.get("OP_UI_URL") or "https://master.tailcf9988.ts.net:10081"

    _, types = api_at(base_url, "GET", f"/api/v3/projects/{PROJECT_ID}/types")
    type_href = None
    for t in types.get("_embedded", {}).get("elements", []):
        name = (t.get("name") or "").lower()
        href = t["_links"]["self"]["href"]
        if name == "task":
            type_href = href
            break
        if type_href is None:
            type_href = href

    _, pris = api_at(base_url, "GET", "/api/v3/priorities")
    prio_href = None
    for p in pris.get("_embedded", {}).get("elements", []):
        if "high" in (p.get("name") or "").lower():
            prio_href = p["_links"]["self"]["href"]
            break

    payload = {
        "subject": SUBJECT,
        "description": {"format": "markdown", "raw": DESCRIPTION.strip()},
        "_links": {
            "project": {"href": f"/api/v3/projects/{PROJECT_ID}"},
            "parent": {"href": f"/api/v3/work_packages/{PARENT_WP_ID}"},
            "status": {"href": "/api/v3/statuses/1"},
        },
    }
    if type_href:
        payload["_links"]["type"] = {"href": type_href}
    if prio_href:
        payload["_links"]["priority"] = {"href": prio_href}

    _, wp = api_at(base_url, "POST", "/api/v3/work_packages", payload)
    wp_id = wp["id"]
    url = f"{ui_url}/work_packages/{wp_id}"
    print(f"CREATED #{wp_id}")
    print(f"URL {url}")

    for rid in RELATED:
        try:
            api_at(
                base_url,
                "POST",
                f"/api/v3/work_packages/{wp_id}/relations",
                {
                    "type": "relates",
                    "_links": {"to": {"href": f"/api/v3/work_packages/{rid}"}},
                },
            )
            print(f"  relates → #{rid}")
        except SystemExit as e:
            print(f"  relate skip #{rid}: {e}")

    try:
        api_at(
            base_url,
            "POST",
            f"/api/v3/work_packages/{wp_id}/activities",
            {
                "comment": {
                    "format": "markdown",
                    "raw": (
                        "WP created for client UAT notes detailed reply package.\n\n"
                        "Next: attach verification report, Playwright evidence, "
                        "per-item Arabic answers.\n\n"
                        "DB focus: `sabry-test` proofs; TR_K19 smoke where relevant."
                    ),
                }
            },
        )
    except SystemExit as e:
        print(f"  activity skip: {e}")

    link_txt = OUT_DIR / "OPENPROJECT_WP_LINK.txt"
    link_txt.write_text(
        f"""OpenProject work package created

ID: #{wp_id}
Subject: {SUBJECT}
Parent: #{PARENT_WP_ID}
Project ID: {PROJECT_ID}

URL: {url}
API: {base_url}/api/v3/work_packages/{wp_id}

Related: #351–#358 (relates)
Created via: docs/op_meeting_nabil/uat_client_reply_wp/create_op_wp.py
""",
        encoding="utf-8",
    )

    index = REPO_DOCS / "OPENPROJECT_WP_LINKS.txt"
    if index.exists():
        with index.open("a", encoding="utf-8") as f:
            f.write(f"\n#{wp_id}  {SUBJECT}\n  {url}\n")

    print(f"Wrote {link_txt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
