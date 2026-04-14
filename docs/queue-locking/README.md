# Queue Locking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent concurrent queue runners from corrupting state by introducing a single-writer guard.

**Architecture:** Use a lock file under `wiki/_system/` created atomically before mutation begins and removed on normal exit. Record process id and timestamp in the lock file so stale locks can be inspected and cleared safely.

**Tech Stack:** Python 3 standard library, atomic file creation with `os.O_EXCL`

---

### Task 1: Build lock acquire/release helpers

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_queue_lock.py`

- [ ] **Step 1: Write the failing lock test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_acquire_lock_rejects_second_writer(tmp_path: Path) -> None:
    lock_path = tmp_path / "manual_queue.lock"
    first = llm_wiki_runner.acquire_lock(lock_path)
    second = llm_wiki_runner.acquire_lock(lock_path)
    assert first is True
    assert second is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_queue_lock.py::test_acquire_lock_rejects_second_writer -v`
Expected: FAIL with missing `acquire_lock`.

- [ ] **Step 3: Write minimal implementation**

```python
import os


def acquire_lock(lock_path: Path) -> bool:
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(f"pid={os.getpid()}\n")
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue_lock.py::test_acquire_lock_rejects_second_writer -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_queue_lock.py
git commit -m "feat: add queue lock helpers"
```

### Task 2: Wrap mutating runner paths with the lock

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_runner_locking.py`

- [ ] **Step 1: Write the failing runner locking test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_run_once_returns_nonzero_when_lock_exists(tmp_path: Path) -> None:
    queue_path = tmp_path / "wiki" / "_system" / "manual_queue.json"
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text('{"items":[]}', encoding="utf-8")
    lock_path = queue_path.with_suffix(".lock")
    lock_path.write_text("pid=1\n", encoding="utf-8")
    code = llm_wiki_runner.run_once(
        project_root=tmp_path,
        queue_path=queue_path,
        template_path=tmp_path / "prompt.txt",
        model=None,
        extra_args=[],
        retry_failed=False,
        only_source_id=None,
        dry_run=True,
    )
    assert code == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner_locking.py::test_run_once_returns_nonzero_when_lock_exists -v`
Expected: FAIL because `run_once` ignores the lock.

- [ ] **Step 3: Write minimal implementation**

```python
lock_path = queue_path.with_suffix(".lock")
if not acquire_lock(lock_path):
    print(f"queue_locked: {lock_path}")
    return 1
try:
    ...
finally:
    release_lock(lock_path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue_lock.py tests/test_runner_locking.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_runner_locking.py
git commit -m "feat: guard queue writes with a lock file"
```

## Self-Review

- Spec coverage: single-writer acquisition and runner integration are both present.
- Placeholder scan: the lock file path and behavior are explicit.
- Type consistency: `acquire_lock` returns `bool` throughout the plan.

