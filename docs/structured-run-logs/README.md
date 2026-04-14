# Structured Run Logs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write structured run logs under `wiki/_system/` so each ingest attempt is inspectable after execution.

**Architecture:** Create one JSON log record per run with start time, source id, command, exit code, and error summary. Keep logs append-only and independent from queue state so operational debugging stays simple.

**Tech Stack:** Python 3 standard library, JSON, filesystem append pattern

---

### Task 1: Add run log writer helpers

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_run_logs.py`

- [ ] **Step 1: Write the failing run log helper test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_append_run_log_writes_jsonl_record(tmp_path: Path) -> None:
    log_path = tmp_path / "run_history.jsonl"
    llm_wiki_runner.append_run_log(log_path, {"source_id": "a", "status": "started"})
    text = log_path.read_text(encoding="utf-8")
    assert '"source_id": "a"' in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run_logs.py::test_append_run_log_writes_jsonl_record -v`
Expected: FAIL with missing `append_run_log`.

- [ ] **Step 3: Write minimal implementation**

```python
def append_run_log(log_path: Path, payload: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run_logs.py::test_append_run_log_writes_jsonl_record -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_run_logs.py
git commit -m "feat: add structured run log writer"
```

### Task 2: Log start and completion for ingest runs

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_run_log_integration.py`

- [ ] **Step 1: Write the failing integration test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_dry_run_creates_start_and_finish_log_records(tmp_path: Path) -> None:
    queue_path = tmp_path / "wiki" / "_system" / "manual_queue.json"
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text(
        '{"items":[{"source_id":"a","title":"A","created_at":"2026-04-14T00:00:00","source_path":"README.md","source_dir":".","wiki_path":"wiki/03_sources/a.md","status":"pending","attempts":0,"updated_at":"","last_error":"","source_hash":"abc"}]}',
        encoding="utf-8",
    )
    prompt_path = tmp_path / "wiki" / "_system" / "manual_runner_prompt.txt"
    prompt_path.write_text("source_id={source_id}", encoding="utf-8")
    code = llm_wiki_runner.run_once(tmp_path, queue_path, prompt_path, None, [], False, None, True)
    log_text = (tmp_path / "wiki" / "_system" / "run_history.jsonl").read_text(encoding="utf-8")
    assert code == 0
    assert '"status": "started"' in log_text
    assert '"status": "finished"' in log_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run_log_integration.py::test_dry_run_creates_start_and_finish_log_records -v`
Expected: FAIL because `run_once` does not write logs.

- [ ] **Step 3: Write minimal implementation**

```python
run_log_path = project_root / "wiki" / "_system" / "run_history.jsonl"
append_run_log(run_log_path, {"status": "started", "source_id": item.source_id, "started_at": now_iso()})
...
append_run_log(
    run_log_path,
    {"status": "finished", "source_id": item.source_id, "finished_at": now_iso(), "exit_code": completed.returncode},
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run_logs.py tests/test_run_log_integration.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_run_log_integration.py
git commit -m "feat: log ingest run lifecycle to jsonl"
```

## Self-Review

- Spec coverage: append-only structured logs and runner integration are both planned.
- Placeholder scan: log file path and record fields are explicit.
- Type consistency: all log records use JSON objects written to `run_history.jsonl`.

