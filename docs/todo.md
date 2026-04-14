# TODO

完成任务时，把对应条目从 `- [ ]` 改为 `- [x]`。

## P0

- [ ] Unify the current scripts into a single CLI entrypoint such as `llm-wiki`.
- [ ] Add terminal-friendly queue commands: `status`, `next`, `failed`, `history`.
- [ ] Add a `doctor` command to validate project structure, required files, and Codex runtime assumptions.
- [ ] Add content-hash based incremental ingest so unchanged sources are skipped safely.
- [ ] Persist per-source processing metadata beyond queue status, including last processed hash, last successful run timestamp, and last output files.
- [ ] Implement a `lint` command for wiki health checks: missing frontmatter, broken source attribution, orphan pages, broken wikilinks, and stale `in_progress` state.
- [ ] Add a lock or single-writer guard for queue execution to avoid concurrent runs corrupting state.
- [ ] Add structured run logs for each ingest pass under `wiki/_system/` so failures are easier to inspect after the fact.

## P1

- [ ] Add a minimal test suite for source discovery, slug generation, queue rebuild, retry logic, and prompt rendering.
- [ ] Add tests for queue crash recovery and stale `in_progress` reset behavior.
- [ ] Create a small demo project fixture under the repository for local verification and documentation examples.
- [ ] Improve scaffold output from `init_llm_wiki.py` with `.gitignore`, system docs, example pages, and sample sources.
- [ ] Add a machine-readable export such as `wiki/_system/source_index.json`.
- [ ] Add a machine-readable page graph export such as `wiki/_system/page_graph.json`.
- [ ] Add a simple `eval` or quality-check command focused on wiki maintenance rules rather than generic RAG metrics.
- [ ] Improve queue observability with summary counts, timestamps, last run duration, and clearer failure reasons.
- [ ] Add a `--json` mode for status and lint commands so other tools and agents can consume the output.
- [ ] Add internal link validation and source file existence checks.

## P2

- [ ] Add optional export formats for downstream agents, such as `llms.txt` or page-level plain text siblings.
- [ ] Add a lightweight query helper over the generated wiki without turning the project into a chat product.
- [ ] Add a simple search index export such as `search-index.json` for local browsing and downstream tooling.
- [ ] Add scheduled-run templates for macOS/Linux so recurring ingest is easier to automate.
- [ ] Add Windows scheduled-run documentation or templates if cross-platform support matters.
- [ ] Add an append-only changelog or roadmap document for repository-level maintenance.
- [ ] Add a simple static-report build that renders wiki health, queue status, and recent ingest activity to Markdown or HTML.
- [ ] Add source import helpers for common formats such as PDF metadata stubs or clipped web pages while keeping manual curation rules intact.

## Later

- [ ] Add folder-level context files so a project can encode local intent or scope hints without changing global schema.
- [ ] Add project-level `overview` generation helpers that summarize current corpus state without overwriting manual pages.
- [ ] Add contradiction surfacing as a first-class report, separated from generic lint findings.
- [ ] Add review queue support for uncertain claims or human judgment calls discovered during ingest.
- [ ] Add page freshness reports based on source age, last ingest time, and confidence.
- [ ] Add optional AI-consumable manifests such as JSON-LD or a build manifest with content hashes.
- [ ] Add optional publish/build workflow for people who want a browsable site from the compiled wiki.
- [ ] Add lightweight MCP or scriptable read-only query tooling over the compiled wiki.

## Not Priority

- [ ] Do not prioritize an Obsidian chat plugin.
- [ ] Do not prioritize a desktop GUI.
- [ ] Do not prioritize vector search or graph visualization before ingest, lint, and testing are stable.
- [ ] Do not prioritize a full static site generator before the CLI workflow is complete.

## Suggested Order

- [ ] CLI unification plus `status` and `doctor`
- [ ] Content-hash incremental ingest
- [ ] `lint` and quality checks
- [ ] Tests and demo fixture
- [ ] Agent-friendly exports
- [ ] Optional query and publishing layer
