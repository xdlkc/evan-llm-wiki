# CLI Entrypoint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current split-script workflow with a single `llm-wiki` CLI entrypoint that exposes initialization and runner operations consistently.

**Architecture:** Introduce a small `llm_wiki_cli.py` module that owns argument parsing and delegates to focused functions in `init_llm_wiki.py` and `llm_wiki_runner.py`. Keep the existing scripts as thin compatibility wrappers during migration so current users are not broken.

**Tech Stack:** Python 3 standard library, `argparse`, existing repository scripts

---

### Task 1: Extract reusable entry functions

**Files:**
- Modify: `scripts/init_llm_wiki.py`
- Modify: `scripts/llm_wiki_runner.py`
- Create: `tests/test_init_entrypoint.py`
- Create: `tests/test_runner_entrypoint.py`

- [ ] **Step 1: Write the failing test for callable init logic**

```python
from pathlib import Path

from scripts import init_llm_wiki


def test_init_main_accepts_argv(tmp_path: Path) -> None:
    code = init_llm_wiki.main(["--project-root", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "wiki" / "index.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_init_entrypoint.py -v`
Expected: FAIL with `TypeError` because `main()` does not accept `argv`.

- [ ] **Step 3: Write minimal implementation**

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize a target project for generic LLM wiki maintenance")
    parser.add_argument("--project-root", required=True, help="target project root")
    parser.add_argument("--force", action="store_true", help="overwrite existing scaffold files")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_init_entrypoint.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/init_llm_wiki.py scripts/llm_wiki_runner.py tests/test_init_entrypoint.py tests/test_runner_entrypoint.py
git commit -m "refactor: expose reusable cli entry functions"
```

### Task 2: Add the unified `llm-wiki` CLI module

**Files:**
- Create: `scripts/llm_wiki_cli.py`
- Create: `tests/test_cli_dispatch.py`

- [ ] **Step 1: Write the failing dispatch test**

```python
from pathlib import Path

from scripts import llm_wiki_cli


def test_cli_dispatches_init_command(tmp_path: Path) -> None:
    code = llm_wiki_cli.main(["init", "--project-root", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "wiki" / "index.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_dispatch.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `main`.

- [ ] **Step 3: Write minimal implementation**

```python
import argparse

from scripts import init_llm_wiki, llm_wiki_runner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="llm-wiki")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--project-root", required=True)
    init_parser.add_argument("--force", action="store_true")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--project-root", default=".")
    run_parser.add_argument("--run-once", action="store_true")
    run_parser.add_argument("--run-all", action="store_true")
    args, extra = parser.parse_known_args(argv)
    if args.command == "init":
        return init_llm_wiki.main(extra + ["--project-root", args.project_root] + (["--force"] if args.force else []))
    return llm_wiki_runner.main(["--project-root", args.project_root] + (["--run-once"] if args.run_once else []) + (["--run-all"] if args.run_all else []))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_dispatch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/llm_wiki_cli.py tests/test_cli_dispatch.py
git commit -m "feat: add unified llm-wiki cli entrypoint"
```

### Task 3: Document and preserve backward compatibility

**Files:**
- Modify: `README.md`
- Modify: `docs/usage.md`

- [ ] **Step 1: Update docs with the new command shape**

```markdown
## Quick start

```bash
python scripts/llm_wiki_cli.py init --project-root /path/to/project
python scripts/llm_wiki_cli.py run --project-root /path/to/project --run-once
```
```

- [ ] **Step 2: Verify docs match actual behavior**

Run: `python scripts/llm_wiki_cli.py --help`
Expected: Shows `init` and `run` subcommands.

- [ ] **Step 3: Run focused regression tests**

Run: `pytest tests/test_init_entrypoint.py tests/test_runner_entrypoint.py tests/test_cli_dispatch.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add README.md docs/usage.md
git commit -m "docs: document unified llm-wiki cli"
```

## Self-Review

- Spec coverage: this plan covers the single entrypoint, dispatch model, and documentation updates.
- Placeholder scan: no `TBD` or omitted file paths remain.
- Type consistency: all tasks use `main(argv: list[str] | None = None) -> int`.

