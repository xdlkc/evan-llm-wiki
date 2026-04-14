#!/usr/bin/env python3
"""Unified CLI entrypoint for llm-wiki commands."""

from __future__ import annotations

import argparse
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_local_module(module_name: str, filename: str):
    module_path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_name} from {module_path}")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


init_llm_wiki = load_local_module("scripts.init_llm_wiki", "init_llm_wiki.py")
llm_wiki_runner = load_local_module("scripts.llm_wiki_runner", "llm_wiki_runner.py")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-wiki", description="Unified CLI for llm-wiki")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize a target project")
    init_parser.add_argument("--project-root", required=True, help="target project root")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing scaffold files")

    run_parser = subparsers.add_parser("run", help="run the manual wiki queue")
    run_parser.add_argument("--project-root", default=".", help="target project root")
    run_parser.add_argument("--run-once", action="store_true", help="process exactly one pending item")
    run_parser.add_argument("--run-all", action="store_true", help="process until queue is exhausted")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        init_args = ["--project-root", args.project_root]
        if args.force:
            init_args.append("--force")
        return init_llm_wiki.main(init_args)

    run_args = ["--project-root", args.project_root]
    if args.run_once:
        run_args.append("--run-once")
    if args.run_all:
        run_args.append("--run-all")
    return llm_wiki_runner.main(run_args)


if __name__ == "__main__":
    raise SystemExit(main())
