#!/usr/bin/env python3
"""Queue runner for one-source-at-a-time manual wiki curation via Codex."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_SOURCE_ROOT = Path("raw/_sources")
DEFAULT_QUEUE_PATH = Path("wiki/_system/manual_queue.json")
DEFAULT_PROMPT_PATH = Path("wiki/_system/manual_runner_prompt.txt")
SOURCE_PAGE_DIR = Path("wiki/03_sources")
PRIMARY_SOURCE_NAMES = (
    "README.md",
    "index.md",
    "content.md",
    "raw.md",
    "raw.txt",
    "raw_content.html",
)
TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".html", ".htm"}
DEFAULT_PROMPT = """Please use the `llm-wiki` skill.

Process exactly this one source item:

- source_id: {source_id}
- title: {title}
- created_at: {created_at}
- source_path: {source_path}
- source_dir: {source_dir}
- target wiki page: {wiki_path}

Requirements:

1. Do not use scripts to generate wiki content.
2. Read the source file directly and curate the wiki manually.
3. If the source directory contains relevant screenshots, charts, diagrams, or images, inspect them before writing.
4. In frontmatter `sources`, prefer only the main human-readable source file, and if `README.md` exists, use only `README.md`.
5. Write or rewrite the corresponding `wiki/03_sources/` page.
6. Update only directly related concept, entity, project, or decision pages.
7. Do not create template-heavy sections that merely restate headings or titles.
8. Update `wiki/index.md` and `wiki/log.md`.
9. Do not modify files under `raw/`.
10. If the current wiki page is low-quality or auto-generated, overwrite it with a manual curated version.
11. At the end, report only the wiki files changed in this pass.
"""


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        payload, end = decoder.raw_decode(raw)
        if raw[end:].strip():
            backup_path = path.with_suffix(path.suffix + ".corrupt")
            if not backup_path.exists():
                backup_path.write_text(raw, encoding="utf-8")
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
        tmp_name = f.name
    os.replace(tmp_name, path)


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def slugify(name: str) -> str:
    text = name.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\-\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "untitled"


@dataclass
class QueueItem:
    source_id: str
    title: str
    created_at: str
    source_path: str
    source_dir: str
    wiki_path: str
    status: str = "pending"
    attempts: int = 0
    updated_at: str = ""
    last_error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "created_at": self.created_at,
            "source_path": self.source_path,
            "source_dir": self.source_dir,
            "wiki_path": self.wiki_path,
            "status": self.status,
            "attempts": self.attempts,
            "updated_at": self.updated_at,
            "last_error": self.last_error,
        }


def choose_primary_source(path: Path) -> Path | None:
    if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
        return path
    if not path.is_dir():
        return None
    for name in PRIMARY_SOURCE_NAMES:
        candidate = path / name
        if candidate.exists():
            return candidate
    for candidate in sorted(path.iterdir()):
        if candidate.is_file() and candidate.suffix.lower() in TEXT_SUFFIXES:
            return candidate
    return None


def discover_sources(project_root: Path, source_root: Path, wiki_root: Path) -> list[QueueItem]:
    root = (project_root / source_root).resolve()
    wiki_source_root = (project_root / wiki_root / "03_sources").resolve()
    items: list[QueueItem] = []
    if not root.exists():
        return items

    for entry in sorted(root.iterdir()):
        primary = choose_primary_source(entry)
        if primary is None:
            continue
        source_id = slugify(entry.stem if entry.is_file() else entry.name)
        title = primary.stem if entry.is_file() else entry.name
        created_at = datetime.fromtimestamp(primary.stat().st_mtime).isoformat(timespec="seconds")
        wiki_path = wiki_source_root / f"{source_id}.md"
        items.append(
            QueueItem(
                source_id=source_id,
                title=title,
                created_at=created_at,
                source_path=str(primary),
                source_dir=str(entry if entry.is_dir() else primary.parent),
                wiki_path=str(wiki_path),
                updated_at=now_iso(),
            )
        )
    items.sort(key=lambda item: (item.created_at, item.source_id))
    return items


def load_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_prompt(template: str, item: QueueItem) -> str:
    return template.format(
        source_id=item.source_id,
        title=item.title,
        created_at=item.created_at,
        source_path=item.source_path,
        source_dir=item.source_dir,
        wiki_path=item.wiki_path,
    )


def build_codex_command(prompt: str, model: str | None, extra_args: list[str]) -> list[str]:
    cmd = ["codex", "exec"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(extra_args)
    cmd.append(prompt)
    return cmd


def next_runnable(items: list[QueueItem], retry_failed: bool, only_source_id: str | None) -> QueueItem | None:
    for item in items:
        if only_source_id is not None and item.source_id != only_source_id:
            continue
        if item.status == "pending":
            return item
        if retry_failed and item.status == "failed":
            return item
    return None


def mark_done(queue_data: dict[str, Any], source_id: str) -> None:
    for item in queue_data["items"]:
        if item["source_id"] == source_id:
            item["status"] = "done"
            item["updated_at"] = now_iso()
            item["last_error"] = ""
            return


def mark_failed(queue_data: dict[str, Any], source_id: str, error: str) -> None:
    for item in queue_data["items"]:
        if item["source_id"] == source_id:
            item["status"] = "failed"
            item["updated_at"] = now_iso()
            item["last_error"] = error[:1000]
            return


def mark_in_progress(queue_data: dict[str, Any], source_id: str) -> None:
    for item in queue_data["items"]:
        if item["source_id"] == source_id:
            item["status"] = "in_progress"
            item["attempts"] = int(item.get("attempts", 0)) + 1
            item["updated_at"] = now_iso()
            item["last_error"] = ""
            return


def reset_in_progress(queue_data: dict[str, Any]) -> None:
    changed = False
    for item in queue_data["items"]:
        if item.get("status") == "in_progress":
            item["status"] = "pending"
            item["updated_at"] = now_iso()
            changed = True
    if changed:
        queue_data["updated_at"] = now_iso()


def ensure_prompt_template(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_PROMPT, encoding="utf-8")


def run_once(
    project_root: Path,
    queue_path: Path,
    template_path: Path,
    model: str | None,
    extra_args: list[str],
    retry_failed: bool,
    only_source_id: str | None,
    dry_run: bool,
) -> int:
    queue_data = read_json(queue_path, {})
    if not queue_data:
        raise SystemExit("queue file missing; run with --rebuild-queue first")

    reset_in_progress(queue_data)
    item = next_runnable(
        [QueueItem(**entry) for entry in queue_data["items"]],
        retry_failed=retry_failed,
        only_source_id=only_source_id,
    )
    if item is None:
        print("queue exhausted")
        return 0

    mark_in_progress(queue_data, item.source_id)
    queue_data["updated_at"] = now_iso()
    write_json(queue_path, queue_data)

    prompt = render_prompt(load_template(template_path), item)
    cmd = build_codex_command(prompt=prompt, model=model, extra_args=extra_args)

    print(f"next_source_id: {item.source_id}")
    print(f"title: {item.title}")
    print(f"source_path: {item.source_path}")
    print(f"wiki_path: {item.wiki_path}")
    print(f"command: {shell_join(cmd)}")

    if dry_run:
        mark_failed(queue_data, item.source_id, "dry_run")
        for entry in queue_data["items"]:
            if entry["source_id"] == item.source_id:
                entry["status"] = "pending"
                entry["last_error"] = ""
                entry["updated_at"] = now_iso()
        queue_data["updated_at"] = now_iso()
        write_json(queue_path, queue_data)
        return 0

    try:
        completed = subprocess.run(cmd, cwd=str(project_root), check=False)
    except Exception as exc:
        mark_failed(queue_data, item.source_id, f"runner exception: {exc}")
        queue_data["updated_at"] = now_iso()
        write_json(queue_path, queue_data)
        return 1

    if completed.returncode == 0:
        mark_done(queue_data, item.source_id)
    else:
        mark_failed(queue_data, item.source_id, f"codex exited with code {completed.returncode}")
    queue_data["updated_at"] = now_iso()
    write_json(queue_path, queue_data)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="One-source-at-a-time manual wiki runner for Codex")
    parser.add_argument("--project-root", default=".", help="target project root")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="source root relative to project root")
    parser.add_argument("--wiki-root", default="wiki", help="wiki root relative to project root")
    parser.add_argument("--queue-file", default=None, help="queue json path; default=wiki/_system/manual_queue.json")
    parser.add_argument("--prompt-template", default=None, help="prompt template path; default=wiki/_system/manual_runner_prompt.txt")
    parser.add_argument("--rebuild-queue", action="store_true", help="rebuild queue from local source files")
    parser.add_argument("--limit", type=int, default=None, help="optional queue rebuild limit")
    parser.add_argument("--run-once", action="store_true", help="process exactly one pending item")
    parser.add_argument("--run-all", action="store_true", help="process until queue is exhausted")
    parser.add_argument("--dry-run", action="store_true", help="show the next Codex command without executing it")
    parser.add_argument("--retry-failed", action="store_true", help="allow failed items to be retried")
    parser.add_argument("--only-source-id", default=None, help="process only the specified source_id")
    parser.add_argument("--model", default=None, help="optional codex model override")
    parser.add_argument("--codex-arg", action="append", default=[], help="extra arg passed to `codex exec`, can be repeated")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    source_root = Path(args.source_root)
    wiki_root = Path(args.wiki_root)
    queue_path = Path(args.queue_file).expanduser().resolve() if args.queue_file else (project_root / wiki_root / "_system" / "manual_queue.json")
    template_path = Path(args.prompt_template).expanduser().resolve() if args.prompt_template else (project_root / wiki_root / "_system" / "manual_runner_prompt.txt")

    ensure_prompt_template(template_path)

    if args.rebuild_queue:
        items = discover_sources(project_root=project_root, source_root=source_root, wiki_root=wiki_root)
        if args.limit is not None:
            items = items[: args.limit]
        payload = {
            "generated_at": now_iso(),
            "updated_at": now_iso(),
            "mode": "manual_single_source",
            "project_root": str(project_root),
            "source_root": str((project_root / source_root).resolve()),
            "wiki_root": str((project_root / wiki_root).resolve()),
            "items": [item.to_dict() for item in items],
        }
        write_json(queue_path, payload)
        print(f"queue_rebuilt: {len(items)}")
        print(f"queue_file: {queue_path}")
        return 0

    if not args.run_once and not args.run_all:
        raise SystemExit("choose one of --rebuild-queue, --run-once, or --run-all")

    if args.run_once:
        return run_once(
            project_root=project_root,
            queue_path=queue_path,
            template_path=template_path,
            model=args.model,
            extra_args=args.codex_arg,
            retry_failed=args.retry_failed,
            only_source_id=args.only_source_id,
            dry_run=args.dry_run,
        )

    while True:
        queue_data = read_json(queue_path, {})
        items = queue_data.get("items", [])
        if not any(
            (
                (args.only_source_id is None or item.get("source_id") == args.only_source_id)
                and item.get("status") in (["pending", "failed"] if args.retry_failed else ["pending"])
            )
            for item in items
        ):
            print("queue exhausted")
            return 0
        code = run_once(
            project_root=project_root,
            queue_path=queue_path,
            template_path=template_path,
            model=args.model,
            extra_args=args.codex_arg,
            retry_failed=args.retry_failed,
            only_source_id=args.only_source_id,
            dry_run=args.dry_run,
        )
        if code != 0:
            return code


if __name__ == "__main__":
    raise SystemExit(main())
