# Runtime vs Git Addons Analysis

**Date:** 2026-06-10  
**Server:** Kafaat / Edafaa Odoo (system Odoo on port 8069)  
**Analysis type:** Read-only — no files, config, or database modified  
**Branch under review:** `feature/student-profile-p1-crs-code`

---

## 1. Executive Summary

| Question | Answer |
|----------|--------|
| What Odoo is actually loading | **`/opt/localaddons`** only (plus core Odoo addons) |
| Is git path scanned? | **No** — `/opt/new_kafaat/custom_addons` is **not** in `addons_path` |
| Are runtime and git identical? | **No** — critical drift in `edafaa_student_profile` security; other shared modules also differ |
| Main risk before UAT | Runtime `security/ir.model.access.csv` is **missing certificate ACLs** that exist in git; fresh install/upgrade from runtime will block student form and certificate access |
| Recommended decision | **Keep `/opt/localaddons` as runtime (Option A)** for immediate UAT; treat **git `custom_addons` as source of truth** for delivered `edafaa_*` modules; **explicit one-way sync** (Option D) before any module upgrade — **do not** add both paths to `addons_path` |

**Bottom line:** Two folders exist on disk for different reasons (live server vs version control). Odoo sees **one** addons tree. The delivered student-profile code is **almost** aligned, but the **runtime security file is behind git**, which already caused UAT issues on `sabry-test` until ACLs were inserted manually in the database.

---

## 2. Runtime Configuration

| Setting | Value |
|---------|-------|
| Config file | `/etc/odoo/odoo.conf` |
| Running process | `/usr/bin/python3 /usr/bin/odoo --config /etc/odoo/odoo.conf --logfile /var/log/odoo/odoo-server.log` |
| Process user | `odoo` (PID observed: 1107606) |
| `addons_path` | `/usr/lib/python3/dist-packages/odoo/addons`, `/opt/localaddons` |
| `/opt/localaddons` in path? | **Yes** |
| `/opt/new_kafaat/custom_addons` in path? | **No** |
| `db_name` in config | **Not set** (multi-database; URL/login selects DB) |
| `logfile` | `/var/log/odoo/odoo.log` (config); process also uses `/var/log/odoo/odoo-server.log` |
| HTTP port | `8069` |
| PostgreSQL databases (sample) | `sabry-test`, `K-19`, `TR_K19`, `training` |
| Docker Odoo | **Not running** (`docker ps` empty). `docker-compose.yml` would use `./custom_addons` on port **10020** if started — separate from live system Odoo |

---

## 3. Module Path Resolution

| Module | Odoo loaded path | Runtime path exists | Git path exists | Notes |
|--------|------------------|---------------------|-----------------|-------|
| `edafaa_student_profile` | `/opt/localaddons/edafaa_student_profile` | Yes | Yes | **Drift** in security CSV |
| `edafaa_student_profile_portal` | `/opt/localaddons/edafaa_student_profile_portal` | Yes | Yes | **Identical** (except `__pycache__`) |
| `student_enrollment_portal` | `/opt/localaddons/student_enrollment_portal` | Yes | Yes | **Major drift** (runtime is superset) |
| `student_lifecycle_dashboard` | `/opt/localaddons/student_lifecycle_dashboard` | Yes | No | Runtime-only |
| `grants_training_suite_v19` | `/opt/localaddons/grants_training_suite_v19` | Yes | Yes | **Drift** (many files) |
| `openeducat_core` | `/opt/localaddons/openeducat_core` | Yes | No | Runtime-only (full OpenEduCat stack) |
| `openeducat_parent` | `/opt/localaddons/openeducat_parent` | Yes | No | Runtime-only |
| `openeducat_library` | `/opt/localaddons/openeducat_library` | Yes | No | Runtime-only |
| `batch_intake` | `/opt/localaddons/batch_intake` | Yes | No | Runtime-only |
| `batch_intake_processor` | *Not found* | No | Yes | Git-only; **not in Apps list** |

---

## 4. Runtime vs Git Diff

| Module | Runtime path | Git path | Status | Critical differences |
|--------|--------------|----------|--------|----------------------|
| `edafaa_student_profile` | `/opt/localaddons/edafaa_student_profile` | `/opt/new_kafaat/custom_addons/edafaa_student_profile` | **Drifted** | `security/ir.model.access.csv`: git has 3 certificate ACL rows; runtime manifest security file does not. Runtime has **orphan** root `ir.model.access.csv` (not in `__manifest__.py`) with certificate ACLs |
| `edafaa_student_profile_portal` | `/opt/localaddons/edafaa_student_profile_portal` | `/opt/new_kafaat/custom_addons/edafaa_student_profile_portal` | **Identical** | Only `__pycache__` differs; both use `op.student` bridge code |
| `student_enrollment_portal` | `/opt/localaddons/student_enrollment_portal` | `/opt/new_kafaat/custom_addons/student_enrollment_portal` | **Drifted** | Runtime has extra models/views (`course.py`, `course_enrollment_request.py`, etc.); multiple manifest, security, and view diffs |
| `grants_training_suite_v19` | `/opt/localaddons/grants_training_suite_v19` | `/opt/new_kafaat/custom_addons/grants_training_suite_v19` | **Drifted** | Controllers, cron, email templates, demo data differ |

**File counts (`edafaa_student_profile`, excluding `__pycache__`):**

- Runtime: 37 files  
- Git: 36 files  
- Common identical: 36 files  
- Only in runtime: `ir.model.access.csv` (root, unused by manifest)  
- Only in git: *(none)*  

---

## 5. File-Level Differences

### `edafaa_student_profile` (student-profile delivery scope)

| Module | File | Difference Type | Runtime Impact | Recommendation |
|--------|------|-----------------|----------------|----------------|
| `edafaa_student_profile` | `security/ir.model.access.csv` | **Content differs** | **Critical** — manifest loads this file; runtime lacks `edafaa.student.certificate` ACLs; student form fails on `certificate_ids` until ACLs exist in DB | **Git is source of truth** — sync this file to runtime before upgrade |
| `edafaa_student_profile` | `ir.model.access.csv` (module root) | **Only in runtime** | **Misleading** — contains certificate ACLs but **not referenced** in `__manifest__.py` `data` list; Odoo upgrade ignores it | Remove or merge into `security/` in a future cleanup (not done in this analysis) |
| `edafaa_student_profile` | `__manifest__.py` | Identical | None | — |
| `edafaa_student_profile` | `models/*.py` | Identical | None | — |
| `edafaa_student_profile` | `views/*.xml` | Identical | None | — |
| `edafaa_student_profile` | `data/*.xml` | Identical | None | — |
| `edafaa_student_profile` | `reports/*.xml` | Identical | None | — |
| `edafaa_student_profile` | `docs/*.md` | Identical | Docs only | No runtime impact |

### `edafaa_student_profile_portal`

| Module | File | Difference Type | Runtime Impact | Recommendation |
|--------|------|-----------------|----------------|----------------|
| `edafaa_student_profile_portal` | All tracked files | **Identical** | None | No sync needed for code |

### Other shared modules (context only)

| Module | Difference Type | Runtime Impact | Recommendation |
|--------|-----------------|----------------|----------------|
| `student_enrollment_portal` | Many code/security/view files differ; runtime is richer | UAT-04 depends on runtime `student.registration` — **use runtime** for portal UAT | Do not sync from git without separate review; out of student-profile P1 scope |
| `grants_training_suite_v19` | Widespread drift | None for student-profile P1 | Defer |

---

## 6. Database Module State

Database queried: **`sabry-test`** (read-only via Odoo shell)

| Module | Installed | Version (`latest_version`) | State | Notes |
|--------|-----------|----------------------------|-------|-------|
| `edafaa_student_profile` | Yes | `19.0.1.0.0` | `installed` | Loaded from `/opt/localaddons` |
| `edafaa_student_profile_portal` | Yes | `19.0.1.0.0` | `installed` | Loaded from `/opt/localaddons` |
| `student_enrollment_portal` | Yes | `19.0.1.0.0` | `installed` | Runtime variant active |
| `student_lifecycle_dashboard` | No | `19.0.1.0.0` | `uninstalled` | Available in Apps from runtime path |
| `grants_training_suite_v19` | No | `19.0.1.0.0` | `uninstalled` | Available in Apps from runtime path |
| `openeducat_core` | Yes | `19.0.1.0` | `installed` | Runtime-only path |
| `openeducat_parent` | Yes | `19.0.1.0` | `installed` | Runtime-only path |
| `openeducat_library` | No | `19.0.1.0` | `uninstalled` | Runtime-only path |
| `batch_intake` | No | `19.0.1.0.0` | `uninstalled` | Runtime-only |
| `batch_intake_processor` | — | — | **Not in Apps list** | Git-only; not on `addons_path` |

**Certificate ACL in database (`sabry-test`):** 3 rows exist for `edafaa.student.certificate` (`access_edafaa_student_certificate_*`). These were **not** loaded from runtime module security on upgrade; they match a **manual/UAT workaround**, not current runtime manifest data.

---

## 7. Git State

| Item | Value |
|------|-------|
| Repo path | `/opt/new_kafaat` |
| Remote | `https://github.com/sabryyoussef/new_kafaat.git` |
| Branch | `feature/student-profile-p1-crs-code` |
| HEAD | `be2e98b55d7c6ad222627a43a7833cf2836c75f4` |
| Remote branch | `be2e98b` (local matches `origin/feature/student-profile-p1-crs-code`) |
| Push status | **Pushed** (local HEAD = remote ref) |
| UAT evidence commit | **Present** — `be2e98b [student-profile] Add Playwright UAT evidence and screenshots` |
| Working tree | Clean for tracked files; **untracked** Playwright tooling (`package.json`, `node_modules`, etc.) — not committed |

**Recent commits (student-profile P1):**

1. `be2e98b` — Playwright UAT evidence  
2. `9e84b18` — UAT checklist and screenshot guide  
3. `9416fd9` — Step 8 certificate workflow  
4. `ec85375` — Step 7 skills tabs  
5. `e197e15` — Step 6 courses tab  
6. `ed21f04` — Step 5 training summary  
7. `fffa46bf` — Step 4 family/siblings  
8. `6463d82` — Step 3B portal bridge  
9. `9b20b3be` — Step 3 required fields  
10. `74c304f5` — Step 2 PRG code  
11. `937ee172` — Step 1 CRS code  

---

## 8. Why Duplicate Apps May Appear

**Evidence-based conclusion: the live Odoo instance should NOT show duplicate apps from both paths.**

| Hypothesis | Evidence |
|------------|----------|
| Both paths in `addons_path` | **Ruled out** — config lists only `/opt/localaddons` + core addons |
| Same technical name scanned twice | **Ruled out** — Odoo scan found **1406 unique** module names; no duplicates across paths |
| Similar but different module names | **Possible confusion only** — e.g. `batch_intake` (runtime) vs `batch_intake_processor` (git-only, not in Apps); `student_enrollment_portal` vs `student_documents_portal` (git-only) |
| Second Odoo / Docker | **Ruled out for port 8069** — Docker not running; system Odoo is sole instance on 8069. Docker compose **would** use `custom_addons` on port 10020 if started |
| Apps list cache | No evidence of stale duplicates in DB; each technical name has one `ir.module.module` row |
| IDE / filesystem vs Odoo Apps | **Likely** — developers see both `/opt/localaddons` and `/opt/new_kafaat/custom_addons` in the editor; Odoo Apps UI does not show filesystem paths |

**What users may perceive as “two custom addons”:**

1. Folder name **`custom_addons`** inside the git repo vs folder name **`localaddons`** on the server — both contain overlapping modules but only **`localaddons`** is wired to Odoo.  
2. Modules that exist in **both** trees with the **same technical name** (4 modules) — Odoo still loads **one** copy from `localaddons`.  
3. **Different** modules with similar purposes (`batch_intake` / `batch_intake_processor`) — appear as separate Apps entries if both were on path; currently only `batch_intake` is scannable.

---

## 9. Decision Options

### Option A — Keep `/opt/localaddons` runtime; git for version control only

| Pros | Cons |
|------|------|
| Lowest risk; current UAT environment works | Manual sync required; drift already proven |
| No `addons_path` change | Wrong file can be edited in git and never reach Odoo |
| Matches production-like layout (full module stack in one tree) | `student_enrollment_portal` and `grants_*` drift unmanaged |

### Option B — Add `/opt/new_kafaat/custom_addons` to `addons_path`

| Pros | Cons |
|------|------|
| Repo directly runnable | **High risk** — 4 modules exist in **both** paths with same technical names; Odoo uses first match only, behavior becomes path-order dependent |
| | Runtime has 53 module dirs vs git 8 — incomplete git tree cannot replace `localaddons` |
| | **Not recommended before UAT** |

### Option C — Symlinks from `localaddons` to git modules

| Pros | Cons |
|------|------|
| Single source for `edafaa_*` | Permissions (`odoo` user), deployment discipline |
| Eliminates drift for linked modules | Only works for modules present in git; rest of stack stays in `localaddons` |
| | Requires testing after each link change |

### Option D — Controlled sync script (`rsync` selected modules)

| Pros | Cons |
|------|------|
| Keeps single `addons_path` | Needs explicit approval and runbook |
| Git → runtime for delivered modules | Overwrites runtime-only hotfixes if any |
| No duplicate-path ambiguity | Requires module upgrade after sync |

---

## 10. Recommendation

### Immediate UAT decision

1. **Do not change `addons_path`.**  
2. **Keep Odoo running from `/opt/localaddons`.**  
3. **Treat git as source of truth** for P1 delivery modules:  
   - `edafaa_student_profile`  
   - `edafaa_student_profile_portal`  
4. **Before client UAT or any `-u edafaa_student_profile` upgrade**, approve a **one-way sync** of git → runtime for those two modules (Option D), with special attention to `security/ir.model.access.csv`.  
5. **Do not sync** `student_enrollment_portal` from git without a separate portal review — runtime variant is what UAT-04 and live portal use.

### Long-term cleanup decision

- Adopt **Option D** (documented rsync/deploy script) for all git-managed modules, **or** **Option C** (symlinks) for `edafaa_*` only.  
- Remove orphan runtime `ir.model.access.csv` at module root after merging certificate ACLs into `security/ir.model.access.csv`.  
- Keep full OpenEduCat / Kafaat stack in `/opt/localaddons`; git repo remains a **subset** for delivered features, not the entire server addons tree.

### What NOT to do

- Do not add both paths to `addons_path`.  
- Do not point Odoo only at `new_kafaat/custom_addons` (missing 45+ runtime modules).  
- Do not assume git and runtime are in sync without `diff`.  
- Do not run module upgrade expecting certificate ACLs from current runtime security file.

---

## 11. Proposed Next Action (plan only — not executed)

| Step | Action | Owner approval |
|------|--------|----------------|
| 1 | **Choose source of truth:** git `custom_addons/edafaa_student_profile*` for P1 delivery | Required |
| 2 | **Sync approved modules** git → `/opt/localaddons` (at minimum `security/ir.model.access.csv` for profile) | Required before upgrade |
| 3 | **Upgrade modules** on `sabry-test`: `-u edafaa_student_profile,edafaa_student_profile_portal` | After sync |
| 4 | **Verify ACLs** in DB from module data (not manual SQL) | After upgrade |
| 5 | **Re-run Playwright UAT** with committed spec; re-seed fixtures | After upgrade |
| 6 | **Capture fresh screenshots** if UI changed | Optional |
| 7 | **Document sync runbook** in repo for future steps | Long-term |
| 8 | **Client UAT** on `sabry-test` with aligned runtime | Final gate |

---

## Appendix A — Module inventory summary

| Category | Count |
|----------|-------|
| Module directories in `/opt/localaddons` | 53 |
| Module directories in `/opt/new_kafaat/custom_addons` | 8 |
| In both (same technical name) | 4 |
| Runtime only (examples) | `openeducat_*`, `batch_intake`, `student_lifecycle_dashboard`, … |
| Git only | `batch_intake_processor`, `student_documents_portal`, `documentation`, `README.md` |

## Appendix B — `edafaa_student_profile` manifest data load order

Runtime and git manifests are identical. Loaded security file:

```text
security/ir.model.access.csv   ← active (runtime version INCOMPLETE)
```

Not loaded:

```text
ir.model.access.csv            ← runtime only; contains certificate ACLs but IGNORED by Odoo
```

---

*End of report — analysis only, no changes made.*
