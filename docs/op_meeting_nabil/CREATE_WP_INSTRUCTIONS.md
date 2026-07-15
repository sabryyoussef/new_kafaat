# Create meeting-requirement work packages in OpenProject

**Source:** Client email (nabil@kafaat.edu.sa, meeting 2026-07-07) — 8 items  
**Parent:** [#87 edafa_kafaat_parent](https://master.tailcf9988.ts.net:10081/work_packages/87)  
**Project:** `wa-120363422104853335` (API id `10`)

## Option A — Script (recommended)

1. OpenProject → avatar → **Access tokens** → create **API** token.
2. From a machine with Tailscale (or master):

```bash
cd /opt/new_kafaat   # or your repo path

export OP_URL="https://master.tailcf9988.ts.net"
export OP_UI_URL="https://master.tailcf9988.ts.net:10081"
export OP_API_KEY="PASTE_TOKEN_HERE"
export OP_PROJECT_ID="10"
export OP_PARENT_WP_ID="87"

python3 docs/op_meeting_nabil/create_openproject_wps.py
```

3. Output: `docs/op_meeting_nabil/OPENPROJECT_WP_LINKS.txt` with all 8 WP URLs.

## Option B — Manual in UI

Open: https://master.tailcf9988.ts.net:10081/projects/wa-120363422104853335/work_packages

Under **#87**, create **8 Tasks** using subjects and descriptions from [`WORK_PACKAGES.md`](WORK_PACKAGES.md).

## Work packages created (8)

| # | Subject |
|---|---------|
| 1 | [Kafaat] Search trainees by national ID (رقم الهوية) |
| 2 | [Kafaat] Student application status on profile (حالة الطالب) |
| 3 | [Kafaat] Voucher Number on student profile |
| 4 | [Kafaat] Batch workflow — Arabic user guide |
| 5 | [Kafaat] Excel bulk assign trainees to sales staff |
| 6 | [Kafaat] Investigate — limited courses visible in system |
| 7 | [Kafaat] Full Arabic UI translation |
| 8 | [Kafaat] Batch attendance with QR code per batch |

Each WP is linked **relates to #86** (trainee profile context) when created via script.
