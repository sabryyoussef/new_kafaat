#!/usr/bin/env python3
"""
Create OpenProject work packages for Kafaat meeting notes (Nabil email, 2026-07-07).

Run from a machine that can reach OpenProject (Tailscale / master):

  export OP_URL="https://master.tailcf9988.ts.net"
  export OP_API_KEY="YOUR_API_KEY"   # OpenProject → Avatar → Access tokens → API
  python3 docs/op_meeting_nabil/create_openproject_wps.py

Optional:
  export OP_UI_URL="https://master.tailcf9988.ts.net:10081"
  export OP_PROJECT_ID="10"
  export OP_PARENT_WP_ID="87"
"""
from __future__ import annotations

import json
import os
import socket as _socket
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

OP_URL = os.environ.get("OP_URL", "https://master.tailcf9988.ts.net").rstrip("/")
OP_UI_URL = os.environ.get("OP_UI_URL", "https://master.tailcf9988.ts.net:10081").rstrip("/")
OP_API_KEY = os.environ.get("OP_API_KEY") or os.environ.get("OPENPROJECT_API_TOKEN") or ""
OP_USER = os.environ.get("OP_USER", "apikey")
PROJECT_ID = int(os.environ.get("OP_PROJECT_ID", "10"))
PARENT_WP_ID = int(os.environ.get("OP_PARENT_WP_ID", "87"))
RELATED_WP_IDS = [int(x) for x in os.environ.get("OP_RELATED_WP_IDS", "86").split(",") if x.strip()]

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs" / "op_meeting_nabil"

MEETING_REF = (
    "Client meeting follow-up (email from nabil@kafaat.edu.sa, 2026-07-07). "
    "Parent: #87 edafa_kafaat_parent."
)

WORK_PACKAGES = [
    {
        "subject": "[Kafaat] Search trainees by national ID (رقم الهوية)",
        "priority": "high",
        "description": f"""## Requirement

Enable searching for trainees/students using **national ID** (`رقم الهوية`) in the Students list.

## Current state (code review)

* Field `id_number` exists on `op.student` (`edafaa_student_profile`)
* List/form show the field; **search view does not** include `id_number`
* Quick search / autocomplete by ID not enabled

## Required work

1. Add `id_number` to `op.student` search view (`student_search_views.xml`)
2. Optional: extend `_rec_names_search` for autocomplete by ID
3. Upgrade module on staging; UAT on TR_K19

## Acceptance criteria

- [ ] User can filter Students by `id_number` from search bar
- [ ] Search works for existing records on staging
- [ ] No regression on other student search filters

## Estimate

0.5 day

## Reference

{MEETING_REF} — Item **1**.
""",
    },
    {
        "subject": "[Kafaat] Student application status on profile (حالة الطالب)",
        "priority": "high",
        "description": f"""## Requirement

Add **student status** on the student profile with these values:

* مقبول (Accepted)
* مرفوض (Rejected)
* تحت المراجعة (Under review)
* ملغي (Cancelled)

## Current state

* `student.registration.state` has a different workflow (draft/submitted/approved/rejected/enrolled)
* `op.student.training_status` = new/active/completed (training lifecycle, not admission status)
* No field on `op.student` with the four client values

## Required work

1. Confirm with client: status on `op.student` vs registration only
2. Add Selection field (e.g. `application_status`) on `op.student`
3. Map from registration/admission paths where applicable
4. Show on form, list, optional search/group-by
5. UAT with Arabic labels

## Acceptance criteria

- [ ] Four statuses available on student profile with Arabic labels
- [ ] Status visible on form and list
- [ ] Mapping documented from registration workflow
- [ ] UAT signed off on staging

## Estimate

2–3 days

## Reference

{MEETING_REF} — Item **2**.
""",
    },
    {
        "subject": "[Kafaat] Voucher Number on student profile",
        "priority": "normal",
        "description": f"""## Requirement

Add **Voucher Number** (`رقم قسيمة الاختبار`) to the student profile.

## Current state

* No `voucher_number` (or equivalent) on `op.student`, `student.registration`, or `op.admission`

## Required work

1. Add `Char` field on `op.student` (and form/list/search as needed)
2. Confirm: manual entry vs import from external system
3. Map from registration finalize if client provides value at intake
4. UAT on staging

## Acceptance criteria

- [ ] Field visible and editable on student profile (Arabic label)
- [ ] Value persists after save and appears in list (if required)
- [ ] Documented entry/import path

## Estimate

0.5 day

## Reference

{MEETING_REF} — Item **3**.
""",
    },
    {
        "subject": "[Kafaat] Batch workflow — Arabic user guide",
        "priority": "normal",
        "description": f"""## Requirement

Provide a clear **Arabic explanation** of how **Batch** intake works and how to use it in the system.

## Current state

* Technical workflow exists: `batch_intake`, `edafaa_batch_intake`, assignment wizard
* No dedicated **client-facing Arabic user guide** for Batch usage

## Required work

1. Document end-to-end flow: upload → validate → schedule batch → process → enrollments
2. Arabic user guide (PDF/HTML/Markdown) with screenshots from staging
3. Note limitations (e.g. CSV vs Excel in base batch_intake)
4. Attach guide to this WP; share with client (WhatsApp/email)

## Acceptance criteria

- [ ] Arabic guide covers create/process batch and trainee assignment
- [ ] Screenshots from Kafaat staging environment
- [ ] Client can follow guide without developer assistance

## Estimate

Documentation only — 1–2 days

## Reference

{MEETING_REF} — Item **4**.
""",
    },
    {
        "subject": "[Kafaat] Excel bulk assign trainees to sales staff",
        "priority": "normal",
        "description": f"""## Requirement

Allow distributing trainee names to **sales staff** by uploading an **Excel** file — not only one-by-one assignment.

## Current state

* `batch_intake` imports trainees from CSV (not sales assignment)
* `batch.trainee.assignment.wizard` assigns selected trainees to a batch (manual)
* No field linking trainee → sales user/employee
* No Excel import for trainee → staff mapping

## Required work

1. Design Excel template (columns TBD with client: trainee identifier + staff email/code)
2. Add `assigned_user_id` or `assigned_employee_id` on `op.student` (or CRM lead link)
3. Import wizard: parse Excel, validate, apply assignments
4. Error report for rejected rows
5. Security + UAT

## Open questions for client

* Column format: name + staff email? national ID + employee code?
* One staff per row or multiple trainees per staff?

## Acceptance criteria

- [ ] Excel template downloadable from system or docs
- [ ] Upload assigns trainees to correct sales staff
- [ ] Rejected rows exported with reason
- [ ] UAT on staging with sample file

## Estimate

5–7 days

## Reference

{MEETING_REF} — Item **5**.
""",
    },
    {
        "subject": "[Kafaat] Investigate — limited courses visible in system",
        "priority": "high",
        "description": f"""## Requirement

Fix or explain why **not all courses** appear in the system (client reports only a subset visible).

## Current state (code review)

* **Not confirmed as code bug** — likely data, domain, or access
* Program → Linked Courses filters by `program_id`
* Standalone Courses menu may be **admin-only** (`edafaa_kafaat_sis`)
* No `ir.rule` limiting `op.course` to two records

## Required work

1. Get exact screen path + screenshot from client
2. Run on TR_K19 (or relevant DB):

```sql
SELECT id, name, code, program_id, active FROM op_course ORDER BY id;
SELECT active, COUNT(*) FROM op_course GROUP BY active;
```

3. Check user groups vs menu access
4. Document root cause: data vs domain vs ACL vs bug
5. Remediation or training doc

## Acceptance criteria

- [ ] Root cause documented (data / domain / ACL / bug)
- [ ] Fix or data remediation applied if needed
- [ ] Client screen re-verified after fix
- [ ] Findings attached to this WP

## Estimate

0.5–1 day (investigation); follow-up WP if code fix required

## Reference

{MEETING_REF} — Item **6**.
""",
    },
    {
        "subject": "[Kafaat] Full Arabic UI translation",
        "priority": "low",
        "description": f"""## Requirement

**Complete Arabic translation** of the user interface for Kafaat SIS/training modules.

## Current state

* OpenEduCat modules have partial `ar_001.po` in runtime addons
* Edafaa custom modules: **no** `i18n/ar_001.po`; mixed hardcoded Arabic in XML
* Many screens remain English when user language is Arabic

## Required work

1. Scope: SIS/student modules only vs full OpenEduCat stack
2. Add `i18n/ar_001.po` for each edafaa module OR migrate to translatable strings
3. Fill gaps in `openeducat_core` Arabic catalog
4. Set default language for Kafaat users if agreed
5. UAT: switch user to Arabic and walk critical flows

## Acceptance criteria

- [ ] Agreed module scope listed in this WP
- [ ] Critical menus/forms show Arabic when user lang = ar_001
- [ ] No mixed EN/AR on student profile, registration, batch, courses (in scope)
- [ ] Translation coverage report attached

## Estimate

2–4 weeks (scope-dependent)

## Reference

{MEETING_REF} — Item **7**.
""",
    },
    {
        "subject": "[Kafaat] Batch attendance with QR code per batch",
        "priority": "low",
        "description": f"""## Requirement

Link **Batch** to **attendance**:

* Generate a unique **QR Code** per batch
* Only students enrolled in that batch can register attendance via QR
* Attendance register based on batch enrollment list

## Current state

* `openeducat_attendance`: manual attendance linked to course + batch
* **No** QR generation, kiosk scan, or portal check-in per batch
* Enterprise attendance modules referenced in config but not deployed

## Required work (high level)

1. Design: student mobile portal vs classroom kiosk
2. `attendance_qr_token` (or similar) on `op.batch` + QR display/print
3. Public/portal endpoint: scan → verify enrollment in batch → write `op.attendance.line`
4. Optional: auto-create attendance register when batch opens
5. Security, audit log, UAT

## Acceptance criteria

- [ ] Each batch has scannable QR (unique, revocable)
- [ ] Non-enrolled student cannot check in via that QR
- [ ] Attendance lines match batch roster
- [ ] UAT scenario documented and passed on staging

## Estimate

3–6 weeks (new feature — separate design WP may be needed)

## Reference

{MEETING_REF} — Item **8**.
""",
    },
]


def api_request(method: str, path: str, data: bytes | None = None, content_type: str | None = None):
    import base64

    url = f"{OP_URL}{path}"
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    token = base64.b64encode(f"{OP_USER}:{OP_API_KEY}".encode()).decode()
    headers["Authorization"] = f"Basic {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} {path}: {err}") from e


def discover_type_href() -> str | None:
    _, types = api_request("GET", f"/api/v3/projects/{PROJECT_ID}/types")
    preferred = ("task", "feature", "delivery")
    found = None
    for t in types.get("_embedded", {}).get("elements", []):
        name = (t.get("name") or "").lower()
        href = t["_links"]["self"]["href"]
        if name in preferred:
            found = href
            if name == "task":
                return href
    return found


def discover_priority_href(name: str) -> str | None:
    _, priorities = api_request("GET", "/api/v3/priorities")
    target = name.lower()
    for p in priorities.get("_embedded", {}).get("elements", []):
        if (p.get("name") or "").lower() == target:
            return p["_links"]["self"]["href"]
    return None


def create_work_package(subject: str, description: str, priority_name: str) -> dict:
    payload = {
        "subject": subject,
        "description": {"format": "markdown", "raw": description.strip()},
        "_links": {
            "project": {"href": f"/api/v3/projects/{PROJECT_ID}"},
            "parent": {"href": f"/api/v3/work_packages/{PARENT_WP_ID}"},
            "status": {"href": "/api/v3/statuses/1"},
        },
    }
    type_href = discover_type_href()
    if type_href:
        payload["_links"]["type"] = {"href": type_href}
    prio_href = discover_priority_href(priority_name)
    if prio_href:
        payload["_links"]["priority"] = {"href": prio_href}

    _, wp = api_request(
        "POST",
        "/api/v3/work_packages",
        data=json.dumps(payload).encode(),
        content_type="application/json",
    )
    return wp


def add_relation(from_id: int, to_id: int, rel_type: str = "relates"):
    payload = {
        "type": rel_type,
        "_links": {"to": {"href": f"/api/v3/work_packages/{to_id}"}},
    }
    try:
        api_request(
            "POST",
            f"/api/v3/work_packages/{from_id}/relations",
            data=json.dumps(payload).encode(),
            content_type="application/json",
        )
    except SystemExit as e:
        print(f"  Relation skip #{from_id} → #{to_id}: {e}")


def main() -> int:
    if not OP_API_KEY:
        print(
            "ERROR: Set OP_API_KEY (OpenProject → Avatar → Access tokens → API).\n"
            f"OP_URL={OP_URL}",
            file=sys.stderr,
        )
        return 1

    status, root = api_request("GET", "/api/v3")
    print(f"OpenProject OK ({status}): {root.get('instanceName', OP_URL)}")
    print(f"Parent #{PARENT_WP_ID} | Project {PROJECT_ID}\n")

    created: list[tuple[int, str, str]] = []
    for i, spec in enumerate(WORK_PACKAGES, 1):
        print(f"[{i}/8] Creating: {spec['subject'][:60]}...")
        wp = create_work_package(spec["subject"], spec["description"], spec["priority"])
        wp_id = wp["id"]
        url = f"{OP_UI_URL}/work_packages/{wp_id}"
        created.append((wp_id, spec["subject"], url))
        print(f"  → #{wp_id} {url}")
        for related in RELATED_WP_IDS:
            add_relation(wp_id, related)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    links_path = OUT_DIR / "OPENPROJECT_WP_LINKS.txt"
    lines = [
        f"Kafaat meeting requirements — {len(created)} work packages under #{PARENT_WP_ID}",
        f"Created via: docs/op_meeting_nabil/create_openproject_wps.py",
        f"Project list: {OP_UI_URL}/projects/wa-120363422104853335/work_packages",
        "",
    ]
    for wp_id, subject, url in created:
        lines.append(f"#{wp_id}  {subject}")
        lines.append(f"  {url}")
        lines.append("")
    links_path.write_text("\n".join(lines), encoding="utf-8")

    print("\n=== ALL WORK PACKAGES CREATED ===")
    for wp_id, subject, url in created:
        print(f"#{wp_id}  {url}")
    print(f"\nSaved: {links_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
