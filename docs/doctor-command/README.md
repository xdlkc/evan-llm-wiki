# Doctor Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `doctor` command that validates project layout, required files, and Codex runtime prerequisites before an ingest run starts.

**Architecture:** Implement a read-only diagnostics layer that checks filesystem expectations and executable availability, then returns a non-zero exit code when required checks fail. Keep checks deterministic and free of network dependence.

**Tech Stack:** Python 3 standard library, `shutil.which`, `pathlib`

---

### Task 1: Build the diagnostics model

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_doctor.py`

- [ ] **Step 1: Write the failing diagnostics test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_doctor_reports_missing_required_paths(tmp_path: Path) -> None:
    checks = llm_wiki_runner.run_doctor(tmp_path)
    assert any(check["status"] == "fail" for check in checks)
    assert any(check["name"] == "raw/_sources exists" for check in checks)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_doctor.py::test_doctor_reports_missing_required_paths -v`
Expected: FAIL with missing `run_doctor`.

- [ ] **Step 3: Write minimal implementation**

```python
def run_doctor(project_root: Path) -> list[dict[str, str]]:
    checks = []
    for rel_path in ("raw/_sources", "wiki", "wiki/_system"):
        path = project_root / rel_path
        checks.append(
            {
                "name": f"{rel_path} exists",
                "status": "pass" if path.exists() else "fail",
                "detail": str(path),
            }
        )
    return checks
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_doctor.py::test_doctor_reports_missing_required_paths -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_doctor.py
git commit -m "feat: add doctor diagnostics model"
```

### Task 2: Add runtime checks and CLI exposure

**Files:**
- Modify: `scripts/llm_wiki_cli.py`
- Modify: `tests/test_cli_dispatch.py`

- [ ] **Step 1: Write the failing CLI doctor test**

```python
from pathlib import Path

from scripts import llm_wiki_cli


def test_cli_doctor_returns_nonzero_for_invalid_project(tmp_path: Path) -> None:
    code = llm_wiki_cli.main(["doctor", "--project-root", str(tmp_path)])
    assert code == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_dispatch.py::test_cli_doctor_returns_nonzero_for_invalid_project -v`
Expected: FAIL because the subcommand does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
import shutil


def codex_check() -> dict[str, str]:
    return {
        "name": "codex executable available",
        "status": "pass" if shutil.which("codex") else "fail",
        "detail": "codex",
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_doctor.py tests/test_cli_dispatch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_cli.py tests/test_cli_dispatch.py
git commit -m "feat: add doctor command"
```

## Self-Review

- Spec coverage: filesystem validation and runtime assumptions are both covered.
- Placeholder scan: no generic “add checks later” language remains.
- Type consistency: all doctor results use `name`, `status`, and `detail`.

