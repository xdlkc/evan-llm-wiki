# Queue Status Commands Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add terminal-friendly queue inspection commands so operators can see current state without opening JSON files.

**Architecture:** Reuse the existing queue JSON file and add read-only reporting helpers that format summary tables and item lists. Expose them as CLI subcommands without mutating queue state.

**Tech Stack:** Python 3 standard library, `json`, `argparse`

---

### Task 1: Add queue summary helpers

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_queue_status.py`

- [ ] **Step 1: Write the failing summary test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_queue_summary_counts_statuses(tmp_path: Path) -> None:
    queue_path = tmp_path / "manual_queue.json"
    queue_path.write_text(
        '{"items":[{"source_id":"a","status":"pending"},{"source_id":"b","status":"failed"}]}',
        encoding="utf-8",
    )
    summary = llm_wiki_runner.summarize_queue(queue_path)
    assert summary["pending"] == 1
    assert summary["failed"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_queue_status.py::test_queue_summary_counts_statuses -v`
Expected: FAIL with `AttributeError` for missing `summarize_queue`.

- [ ] **Step 3: Write minimal implementation**

```python
def summarize_queue(queue_path: Path) -> dict[str, int]:
    queue_data = read_json(queue_path, {"items": []})
    summary = {"pending": 0, "in_progress": 0, "done": 0, "failed": 0}
    for item in queue_data["items"]:
        status = item.get("status", "pending")
        summary[status] = summary.get(status, 0) + 1
    return summary
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue_status.py::test_queue_summary_counts_statuses -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_queue_status.py
git commit -m "feat: add queue summary helpers"
```

### Task 2: Add `status`, `next`, `failed`, and `history` commands

**Files:**
- Modify: `scripts/llm_wiki_cli.py`
- Modify: `scripts/llm_wiki_runner.py`
- Modify: `tests/test_cli_dispatch.py`

- [ ] **Step 1: Write the failing CLI status test**

```python
from pathlib import Path

from scripts import llm_wiki_cli


def test_cli_status_command_prints_summary(tmp_path: Path, capsys) -> None:
    queue_path = tmp_path / "wiki" / "_system" / "manual_queue.json"
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text('{"items":[{"source_id":"a","status":"pending"}]}', encoding="utf-8")
    code = llm_wiki_cli.main(["status", "--project-root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "pending: 1" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_dispatch.py::test_cli_status_command_prints_summary -v`
Expected: FAIL because the `status` subcommand does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def print_queue_status(queue_path: Path) -> None:
    summary = summarize_queue(queue_path)
    for key in ("pending", "in_progress", "done", "failed"):
        print(f"{key}: {summary.get(key, 0)}")


def list_queue_items(queue_path: Path, status: str | None = None) -> list[dict[str, Any]]:
    queue_data = read_json(queue_path, {"items": []})
    items = queue_data["items"]
    if status is not None:
        items = [item for item in items if item.get("status") == status]
    return items
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue_status.py tests/test_cli_dispatch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_cli.py scripts/llm_wiki_runner.py tests/test_cli_dispatch.py
git commit -m "feat: add queue inspection commands"
```

## Self-Review

- Spec coverage: all four queue inspection commands are represented.
- Placeholder scan: each step includes exact commands and code.
- Type consistency: command handlers read from queue JSON without mutation.

