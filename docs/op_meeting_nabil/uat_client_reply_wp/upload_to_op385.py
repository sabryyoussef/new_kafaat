#!/usr/bin/env python3
"""Upload UAT client-reply evidence pack to OpenProject WP #385."""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import ssl
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parent
WP_ID = int(os.environ.get("OP_WP_ID", "385"))
BASE = (
    os.environ.get("OP_URL")
    or os.environ.get("OPENPROJECT_BASE_URL")
    or "https://projects.drpaws.ai"
).rstrip("/")
TOKEN = (
    os.environ.get("OP_API_KEY") or os.environ.get("OPENPROJECT_API_TOKEN") or ""
).strip()
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

SHOT_MAP = {
    "01_search_by_id.png": "s1_351_search_by_id_number.png",
    "02_application_status.png": "s2_352_student_form_application_status.png",
    "03_voucher_number.png": "s1_353_student_form_voucher.png",
    "04_batch_intakes.png": "s2_354_batch_intakes_list.png",
    "05_excel_assign_wizard.png": "s3_355_excel_assign_wizard.png",
    "06_courses_list.png": "s1_356_admin_courses_list.png",
    "08_batch_qr.png": "s5_358_batch_form_qr.png",
    "08b_checkin_success.png": "s5_358_checkin_success.png",
    "08c_no_active_session.png": "s5_358_no_active_session.png",
}

SRC_SHOTS = PACK.parent / "evidence" / "screenshots"
OUT_SHOTS = PACK / "evidence" / "screenshots"


def ssl_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def api(method: str, path: str, data: bytes | None = None, content_type: str | None = None):
    auth = base64.b64encode(f"apikey:{TOKEN}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "User-Agent": UA,
    }
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120, context=ssl_ctx()) as resp:
            body = resp.read()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} {path}: {err[:600]}") from e


def mirror_screenshots():
    OUT_SHOTS.mkdir(parents=True, exist_ok=True)
    for dest, src_name in SHOT_MAP.items():
        src = SRC_SHOTS / src_name
        if not src.is_file():
            print(f"MISSING screenshot source: {src}")
            continue
        (OUT_SHOTS / dest).write_bytes(src.read_bytes())
        print(f"mirrored {dest}")


def build_zip() -> Path:
    zip_path = PACK / "UAT_CLIENT_REPLY_EVIDENCE_PACK.zip"
    include = [
        PACK / "CLIENT_REPLY_DETAILED_AR_EN.md",
        PACK / "WHATSAPP_UAT_NOTES_REPLY_AR.txt",
        PACK / "KAFAAT_UAT_NOTES_VERIFICATION_REPORT.md",
        PACK / "OPENPROJECT_WP_LINK.txt",
        PACK / "guides" / "USER_GUIDE_BATCH_AR.md",
    ]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in include:
            if p.is_file():
                zf.write(p, arcname=p.relative_to(PACK).as_posix())
        for png in sorted(OUT_SHOTS.glob("*.png")):
            zf.write(png, arcname=f"evidence/screenshots/{png.name}")
    print(f"zip {zip_path} ({zip_path.stat().st_size} bytes)")
    return zip_path


def upload_file(wp_id: int, file_path: Path, description: str = ""):
    boundary = "----OpBoundaryUatReply385"
    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    meta = json.dumps(
        {
            "fileName": file_path.name,
            "description": {"format": "plain", "raw": description or file_path.name},
        }
    )
    file_bytes = file_path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="metadata"\r\n'
        f"Content-Type: application/json\r\n\r\n"
        f"{meta}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()
    api(
        "POST",
        f"/api/v3/work_packages/{wp_id}/attachments",
        data=body,
        content_type=f"multipart/form-data; boundary={boundary}",
    )
    print(f"attached {file_path.name}")


def post_comment(wp_id: int):
    comment = """## UAT client reply pack delivered

Detailed item-by-item reply (AR+EN) + Playwright screenshots attached.

| # | Verdict | Screenshot |
|---|---------|------------|
| 1 Search by ID | Done / implemented | `01_search_by_id.png` |
| 2 Student status | Editable (`application_status`) — not Training Status | `02_application_status.png` |
| 3 Voucher | Present on student form | `03_voucher_number.png` |
| 4 Offline Batch | Batch Intake + Arabic guide | `04_batch_intakes.png` |
| 5 Excel → sales | Under **Students**, not Contact Pools | `05_excel_assign_wizard.png` |
| 6 Courses visibility | Ops/ACL/`program_id` | `06_courses_list.png` |
| 7 Full Arabic | Partial — open S4/#357 | (no full i18n claim) |
| 8 Batch QR | Installed; needs session + Generate QR (TR_K19: 0 QR yet) | `08_batch_qr.png` |

**Pack:** `UAT_CLIENT_REPLY_EVIDENCE_PACK.zip`  
**WhatsApp draft:** `WHATSAPP_UAT_NOTES_REPLY_AR.txt`  
**DB:** `sabry-test` proofs; TR_K19 notes for #8.
"""
    api(
        "POST",
        f"/api/v3/work_packages/{wp_id}/activities",
        data=json.dumps({"comment": {"format": "markdown", "raw": comment}}).encode(),
        content_type="application/json",
    )
    print("comment posted")


def main() -> int:
    if not TOKEN:
        print("ERROR: OPENPROJECT_API_TOKEN / OP_API_KEY required", file=sys.stderr)
        return 1
    st, root = api("GET", "/api/v3")
    print(f"OP OK {st} {root.get('instanceName')} → WP #{WP_ID}")
    mirror_screenshots()
    zip_path = build_zip()

    upload_file(WP_ID, PACK / "CLIENT_REPLY_DETAILED_AR_EN.md", "Detailed AR+EN reply")
    upload_file(WP_ID, PACK / "WHATSAPP_UAT_NOTES_REPLY_AR.txt", "WhatsApp summary draft")
    upload_file(WP_ID, PACK / "KAFAAT_UAT_NOTES_VERIFICATION_REPORT.md", "Full verification report")
    upload_file(WP_ID, PACK / "guides" / "USER_GUIDE_BATCH_AR.md", "Batch Arabic user guide")
    upload_file(WP_ID, zip_path, "Full evidence zip")
    for png in sorted(OUT_SHOTS.glob("*.png")):
        upload_file(WP_ID, png, f"Screenshot {png.name}")
    post_comment(WP_ID)
    print(f"Done: {BASE}/work_packages/{WP_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
