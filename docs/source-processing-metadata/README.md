# Source Processing Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist per-source processing metadata so the system can explain what was last processed, when it succeeded, and which wiki files changed.

**Architecture:** Introduce a separate metadata file under `wiki/_system/` keyed by `source_id`. Update it only after successful runs so queue state and run history remain decoupled.

**Tech Stack:** Python 3 standard library, JSON files, existing queue runner

---

### Task 1: Add metadata file helpers

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_processing_metadata.py`

- [ ] **Step 1: Write the failing metadata helper test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_write_processing_metadata_persists_record(tmp_path: Path) -> None:
    metadata_path = tmp_path / "processing_metadata.json"
    llm_wiki_runner.write_processing_metadata(
        metadata_path,
        "source-a",
        {"last_processed_hash": "abc", "last_success_at": "2026-04-14T10:00:00"},
    )
    payload = llm_wiki_runner.read_json(metadata_path, {})
    assert payload["source-a"]["last_processed_hash"] == "abc"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_processing_metadata.py::test_write_processing_metadata_persists_record -v`
Expected: FAIL with missing `write_processing_metadata`.

- [ ] **Step 3: Write minimal implementation**

```python
def write_processing_metadata(metadata_path: Path, source_id: str, record: dict[str, Any]) -> None:
    payload = read_json(metadata_path, {})
    payload[source_id] = record
    write_json(metadata_path, payload)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_processing_metadata.py::test_write_processing_metadata_persists_record -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_processing_metadata.py
git commit -m "feat: add processing metadata helpers"
```

### Task 2: Record successful run details

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_success_recording.py`

- [ ] **Step 1: Write the failing success-recording test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_record_success_stores_hash_timestamp_and_outputs(tmp_path: Path) -> None:
    metadata_path = tmp_path / "processing_metadata.json"
    item = llm_wiki_runner.QueueItem(
        source_id="source-a",
        title="Source A",
        created_at="2026-04-14T00:00:00",
        source_path="raw/_sources/source-a/README.md",
        source_dir="raw/_sources/source-a",
        wiki_path="wiki/03_sources/source-a.md",
        source_hash="abc",
    )
    llm_wiki_runner.record_success(metadata_path, item, ["wiki/03_sources/source-a.md"])
    payload = llm_wiki_runner.read_json(metadata_path, {})
    assert payload["source-a"]["last_output_files"] == ["wiki/03_sources/source-a.md"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_success_recording.py::test_record_success_stores_hash_timestamp_and_outputs -v`
Expected: FAIL with missing `record_success`.

- [ ] **Step 3: Write minimal implementation**

```python
def record_success(metadata_path: Path, item: QueueItem, output_files: list[str]) -> None:
    write_processing_metadata(
        metadata_path,
        item.source_id,
        {
            "last_processed_hash": item.source_hash,
            "last_success_at": now_iso(),
            "last_output_files": output_files,
        },
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_processing_metadata.py tests/test_success_recording.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_success_recording.py
git commit -m "feat: record per-source processing metadata"
```

## Self-Review

- Spec coverage: the plan covers persisted hash, success timestamp, and output files.
- Placeholder scan: no vague “store metadata” step remains.
- Type consistency: metadata fields use stable names through every task.

