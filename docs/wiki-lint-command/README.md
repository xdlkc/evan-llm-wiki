# Wiki Lint Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `lint` command that checks core wiki health rules before knowledge quality drifts too far.

**Architecture:** Implement focused lint checks over Markdown files and queue state, returning structured findings with severity, file path, and rule id. Start with deterministic checks only: frontmatter, source attribution, wikilinks, orphan pages, and stale queue items.

**Tech Stack:** Python 3 standard library, `pathlib`, regex, Markdown-as-text parsing

---

### Task 1: Build lint result primitives

**Files:**
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_lint.py`

- [ ] **Step 1: Write the failing lint test**

```python
from pathlib import Path

from scripts import llm_wiki_runner


def test_lint_frontmatter_flags_missing_sources(tmp_path: Path) -> None:
    page = tmp_path / "wiki" / "03_sources" / "a.md"
    page.parent.mkdir(parents=True)
    page.write_text("---\nupdated_at: 2026-04-14\nconfidence: medium\n---\n", encoding="utf-8")
    findings = llm_wiki_runner.lint_frontmatter(page)
    assert findings[0]["rule"] == "missing_sources"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_lint.py::test_lint_frontmatter_flags_missing_sources -v`
Expected: FAIL with missing `lint_frontmatter`.

- [ ] **Step 3: Write minimal implementation**

```python
def lint_frontmatter(page_path: Path) -> list[dict[str, str]]:
    text = page_path.read_text(encoding="utf-8")
    findings = []
    if "sources:" not in text:
        findings.append({"rule": "missing_sources", "path": str(page_path), "severity": "error"})
    return findings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_lint.py::test_lint_frontmatter_flags_missing_sources -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_runner.py tests/test_lint.py
git commit -m "feat: add lint result primitives"
```

### Task 2: Implement lint checks and CLI command

**Files:**
- Modify: `scripts/llm_wiki_cli.py`
- Modify: `scripts/llm_wiki_runner.py`
- Modify: `tests/test_cli_dispatch.py`

- [ ] **Step 1: Write the failing CLI lint test**

```python
from pathlib import Path

from scripts import llm_wiki_cli


def test_cli_lint_returns_nonzero_on_error(tmp_path: Path) -> None:
    page = tmp_path / "wiki" / "03_sources" / "a.md"
    page.parent.mkdir(parents=True)
    page.write_text("no frontmatter", encoding="utf-8")
    code = llm_wiki_cli.main(["lint", "--project-root", str(tmp_path)])
    assert code == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_dispatch.py::test_cli_lint_returns_nonzero_on_error -v`
Expected: FAIL because the subcommand does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def run_lint(project_root: Path) -> list[dict[str, str]]:
    findings = []
    for page_path in sorted((project_root / "wiki").rglob("*.md")):
        findings.extend(lint_frontmatter(page_path))
        findings.extend(lint_wikilinks(page_path, project_root / "wiki"))
    findings.extend(lint_orphans(project_root / "wiki"))
    findings.extend(lint_stale_queue(project_root / "wiki" / "_system" / "manual_queue.json"))
    return findings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_lint.py tests/test_cli_dispatch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_cli.py scripts/llm_wiki_runner.py tests/test_cli_dispatch.py
git commit -m "feat: add wiki lint command"
```

## Self-Review

- Spec coverage: frontmatter, attribution, wikilinks, orphans, and stale queue items are included.
- Placeholder scan: each lint rule is named directly.
- Type consistency: findings use `rule`, `path`, and `severity`.

