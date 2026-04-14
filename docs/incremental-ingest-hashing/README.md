# Incremental Ingest Hashing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Skip unchanged sources safely by comparing current content hashes to the last processed version.

**Architecture:** Compute a stable hash for each primary source during queue rebuild, store it on queue items, and compare it against persisted processing metadata before selecting runnable work. Keep the hash scope limited to the primary source file for the first version.

**Tech Stack:** Python 3 standard library, `hashlib`, existing queue JSON

---

### Task 1: Add source hashing at discovery time

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_source_hashing.py`

- [ ] **Step 1: Write the failing hashing test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_compute_source_hash_changes_with_file_content(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text("alpha", encoding="utf-8")
    first = llm_wiki_runner.compute_source_hash(source)
    source.write_text("beta", encoding="utf-8")
    second = llm_wiki_runner.compute_source_hash(source)
    assert first != second
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_source_hashing.py::test_compute_source_hash_changes_with_file_content -v`
Expected: FAIL with missing `compute_source_hash`.

- [ ] **Step 3: Write minimal implementation**

```python
import hashlib


def compute_source_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_source_hashing.py::test_compute_source_hash_changes_with_file_content -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_source_hashing.py
git commit -m "feat: add primary source hashing"
```

### Task 2: Skip unchanged items during queue rebuild and selection

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_incremental_queue.py`

- [ ] **Step 1: Write the failing incremental queue test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_next_runnable_skips_item_with_matching_processed_hash() -> None:
    items = [
        llm_wiki_runner.QueueItem(
            source_id="a",
            title="A",
            created_at="2026-01-01T00:00:00",
            source_path="raw/_sources/a/README.md",
            source_dir="raw/_sources/a",
            wiki_path="wiki/03_sources/a.md",
            source_hash="same",
            status="pending",
        )
    ]
    metadata = {"a": {"last_processed_hash": "same"}}
    item = llm_wiki_runner.next_runnable(items, retry_failed=False, only_source_id=None, metadata=metadata)
    assert item is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_incremental_queue.py::test_next_runnable_skips_item_with_matching_processed_hash -v`
Expected: FAIL because `QueueItem` lacks `source_hash` and `next_runnable` lacks `metadata`.

- [ ] **Step 3: Write minimal implementation**

```python
@dataclass
class QueueItem:
    ...
    source_hash: str = ""


def should_skip_item(item: QueueItem, metadata: dict[str, Any]) -> bool:
    record = metadata.get(item.source_id, {})
    return bool(item.source_hash and item.source_hash == record.get("last_processed_hash"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_source_hashing.py tests/test_incremental_queue.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_incremental_queue.py
git commit -m "feat: skip unchanged sources during queue selection"
```

## Self-Review

- Spec coverage: hash generation and skip logic are both included.
- Placeholder scan: implementation details are explicit.
- Type consistency: the plan uses `source_hash` and `last_processed_hash` consistently.

