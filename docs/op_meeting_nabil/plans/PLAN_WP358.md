# Development Plan — OP#358 / Odoo #49

**Superseded by the full implementation plan:**

→ **[IMPLEMENTATION_PLAN_S5_WP358.md](IMPLEMENTATION_PLAN_S5_WP358.md)**

Use that document for execution. Summary of locked design:

| Topic | Choice |
|-------|--------|
| Check-in UX | **1A — Student portal (phone)** |
| QR lifetime | **Stable per batch** (regenerate/revoke) |
| Late policy | After **session start**; grace **15 minutes** → then Late |
| Foundation | Reuse `openeducat_attendance` + active `op.session` |

**Module:** `edafaa_batch_attendance` · **Branch:** `feature/meeting-s5-358` · **Sprint:** S5
