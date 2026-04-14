#!/usr/bin/env python3
"""Scaffold a target project for generic LLM wiki maintenance."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
COPY_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    ".codex/skills/llm-wiki/SKILL.md",
    "schema/policy.md",
    "schema/workflows.md",
]
DIRECTORIES = [
    "raw/_sources",
    "raw/_attachments",
    "wiki/00_overview",
    "wiki/01_entities",
    "wiki/02_concepts",
    "wiki/03_sources",
    "wiki/04_projects",
    "wiki/05_decisions",
    "wiki/_system",
    "schema",
]
STATIC_FILES = {
    "wiki/index.md": "# Wiki Index\n\n## Overview\n\n- Start here.\n",
    "wiki/log.md": "# Wiki Log\n",
    "wiki/_system/manual_runner_prompt.txt": """Please use the `llm-wiki` skill.

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
""",
}


def write_if_missing(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize a target project for generic LLM wiki maintenance")
    parser.add_argument("--project-root", required=True, help="target project root")
    parser.add_argument("--force", action="store_true", help="overwrite existing scaffold files")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).expanduser().resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    for rel in DIRECTORIES:
        (project_root / rel).mkdir(parents=True, exist_ok=True)

    for rel in COPY_FILES:
        src = TEMPLATE_ROOT / rel
        dst = project_root / rel
        write_if_missing(dst, src.read_text(encoding="utf-8"), force=args.force)

    for rel, content in STATIC_FILES.items():
        write_if_missing(project_root / rel, content, force=args.force)

    print(f"initialized: {project_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
