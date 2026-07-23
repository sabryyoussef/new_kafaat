#!/usr/bin/env python3
"""Create Odoo mirror task under parent #41 for OP#385 UAT client reply pack."""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

import xmlrpc.client

URL = "http://127.0.0.1:8069"
DB = "sabry-test"
USER = "admin"
PASSWORD = "admin"
PARENT_ID = 41
PROJECT_ID = 3
PACK = Path("/opt/new_kafaat/docs/op_meeting_nabil/uat_client_reply_wp")

DESCRIPTION = """
<p><b>OpenProject:</b> <a href="https://projects.drpaws.ai/work_packages/385">#385</a>
— UAT notes client reply (detailed proof + Playwright screenshots)</p>
<p><b>Parent OP:</b> #87 · Related: #351–#358</p>
<h3>Verdict summary</h3>
<ol>
<li>Search by ID — Done</li>
<li>Student status — editable (not Training Status)</li>
<li>Voucher — present on form</li>
<li>Offline Batch — Batch Intake + Arabic guide</li>
<li>Excel→sales — under Students (not Contact Pools)</li>
<li>Courses visibility — ops/ACL/program_id</li>
<li>Full Arabic — partial, open S4/#357</li>
<li>Batch QR — installed; needs session + Generate QR on TR_K19</li>
</ol>
<p>See attachments: CLIENT_REPLY_DETAILED_AR_EN.md + evidence zip.</p>
"""


def main() -> int:
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if not uid:
        raise SystemExit("Odoo auth failed")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def kw(model, method, *args, **kwargs):
        return models.execute_kw(DB, uid, PASSWORD, model, method, list(args), kwargs)

    existing = kw(
        "project.task",
        "search_read",
        [["name", "ilike", "OP#385"], ["project_id", "=", PROJECT_ID]],
        fields=["id", "name"],
        limit=1,
    )
    if existing:
        task_id = existing[0]["id"]
        print(f"reuse task #{task_id}")
        kw("project.task", "write", [task_id], {"description": DESCRIPTION})
    else:
        task_id = kw(
            "project.task",
            "create",
            {
                "name": "OP#385 — UAT notes client reply (proof + Playwright screenshots)",
                "project_id": PROJECT_ID,
                "parent_id": PARENT_ID,
                "description": DESCRIPTION,
            },
        )
        print(f"created task #{task_id}")

    files = [
        PACK / "CLIENT_REPLY_DETAILED_AR_EN.md",
        PACK / "WHATSAPP_UAT_NOTES_REPLY_AR.txt",
        PACK / "KAFAAT_UAT_NOTES_VERIFICATION_REPORT.md",
        PACK / "guides" / "USER_GUIDE_BATCH_AR.md",
        PACK / "UAT_CLIENT_REPLY_EVIDENCE_PACK.zip",
    ]
    files += sorted((PACK / "evidence" / "screenshots").glob("*.png"))

    for path in files:
        if not path.is_file():
            print(f"skip missing {path.name}")
            continue
        # avoid duplicate same name on re-run
        dup = kw(
            "ir.attachment",
            "search",
            [
                ["res_model", "=", "project.task"],
                ["res_id", "=", task_id],
                ["name", "=", path.name],
            ],
            limit=1,
        )
        if dup:
            print(f"attach exists {path.name}")
            continue
        data = base64.b64encode(path.read_bytes()).decode()
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        att_id = kw(
            "ir.attachment",
            "create",
            {
                "name": path.name,
                "datas": data,
                "res_model": "project.task",
                "res_id": task_id,
                "mimetype": mime,
            },
        )
        print(f"attached #{att_id} {path.name}")

    kw(
        "mail.message",
        "create",
        {
            "model": "project.task",
            "res_id": task_id,
            "body": (
                "<p>UAT client reply evidence pack mirrored from OP#385. "
                "Playwright S1/S2/S3/S5 green on sabry-test.</p>"
            ),
            "message_type": "comment",
            "subtype_id": 1,
        },
    )

    link = f"{URL}/web#id={task_id}&model=project.task&view_type=form&db={DB}"
    out = PACK / "ODOO_TASK_LINK.txt"
    out.write_text(
        f"Odoo task #{task_id}\n{link}\nParent: #{PARENT_ID}\nOP: #385\n",
        encoding="utf-8",
    )
    print(link)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
