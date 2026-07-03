# Delete Student Proof — `op.student` unlink on Kafaat (TR_K19)

**Date:** 2026-06-15 15:35 UTC  
**Environment:** `erp.kafaat.edu.sa`  
**Database:** `TR_K19` (كفاءات)  
**Fix:** `openeducat_parent/models/parent.py` — safe `child_ids` sync on unlink  

---

## Result: SUCCESS

| Check | Result |
|-------|--------|
| Test student created with parent link | **Yes** (student id=8084, parent id=1) |
| Parent portal user with `child_ids` | **Yes** — `[26]` before delete |
| `student.unlink()` | **SUCCESS** — no `ValueError` |
| Student exists after delete | **No** |
| Parent `child_ids` after delete | **`[]`** (correctly cleared) |
| Shell exit code | **0** |

---

## Scenario tested (reproduces original bug)

The original error on `portal.ibdaa.academy`:

```
ValueError: list.remove(x): x not in list
File: openeducat_parent/models/parent.py, unlink
```

We recreated the **worst-case** scenario:

1. Created test student with required profile fields
2. Created parent linked to student (`parent_ids` / `student_ids`)
3. Created portal user for student (`user_id=26`)
4. Created parent user with `child_ids=[26]`
5. Deleted student via `unlink()`

**Outcome:** Delete succeeded. Parent `child_ids` rebuilt to `[]`.

---

## Proof output (automated test)

```
--- Step 4: Create portal user for student (worst-case child_ids scenario) ---
student user_id=26
parent user_id=27, child_ids BEFORE delete=[26]

--- Step 5: Delete student (unlink) ---
DELETE RESULT: SUCCESS

--- Step 6: Post-delete verification ---
Student record exists after delete: op.student()
parent child_ids AFTER delete=[]
Remaining test students: []
VERIFICATION: PASS
Shell exit: 0
```

---

## Comparison

| | Before fix | After fix (2026-06-15) |
|---|-----------|------------------------|
| Delete student with parent | `ValueError: list.remove(x): x not in list` | **SUCCESS** |
| Parent `child_ids` sync | Crash | Rebuilt safely to `[]` |

---

## Notes

- Test used disposable records (`DELETE PROOF Student`, `DELPROOF-20260615`) — cleaned up after test.
- No production student data was deleted.
- Test data: parent id=1 may remain if cleanup ran; student id=8084 was deleted.

---

*Full raw log: `delete_student_run.log` in this folder.*
