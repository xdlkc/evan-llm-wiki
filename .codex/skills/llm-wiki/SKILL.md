---
name: llm-wiki
description: Build and maintain a generic Markdown-first wiki from local source material by directly editing wiki pages. Use this whenever the user asks to ingest, curate, refresh, compile, reorganize, or maintain a local LLM wiki from source files, especially with one-source-at-a-time manual curation.
---

# Generic LLM Wiki Skill

Use this skill when the model should act as the wiki maintainer.

## Read first

1. `AGENTS.md`
2. `CLAUDE.md` if present
3. `schema/policy.md` if present
4. `schema/workflows.md` if present
5. the affected source files under `raw/`

## Source of truth

Only read from raw sources under `raw/`.
Do not edit any of them.

## Output locations

Write durable knowledge into:

1. `wiki/00_overview/`
2. `wiki/01_entities/`
3. `wiki/02_concepts/`
4. `wiki/03_sources/`
5. `wiki/04_projects/`
6. `wiki/05_decisions/`
7. `wiki/index.md`
8. `wiki/log.md`

## Attribution rules

1. Prefer one primary human-readable source file in frontmatter.
2. If the source item has `README.md`, list only `README.md` in `sources`.
3. Use HTML, JSON, screenshots, and attachments to improve understanding when needed, but do not list them in `sources` unless the project explicitly asks for that.

## Required reading behavior

1. Read the primary source file directly.
2. If the source directory includes screenshots, charts, diagrams, or other images that materially affect meaning, inspect them before writing.
3. Use images to understand structure, process, evidence, tables, or visual outcomes.
4. If an image is ambiguous or unreadable, say so explicitly.

## Workflow

1. Read the relevant source item and check whether matching wiki pages already exist.
2. Inspect relevant images or attachments if they matter.
3. Prefer updating existing pages over creating near-duplicates.
4. Edit the wiki Markdown files directly.
5. Keep every synthesized claim traceable to source files.
6. Refresh links, indexes, and log pages in the same maintenance pass.
7. After the update, summarize which wiki files changed.

## Content rules

1. Preserve source attribution in frontmatter and body.
2. Mark uncertain or weakly supported statements explicitly.
3. Concept pages should represent durable concepts.
4. Entity pages should only exist for repeated entities.
5. Decision pages should summarize tradeoffs or actions, not duplicate source text.

## Non-negotiable writing rules

1. Do not use scripts to generate wiki content.
2. Do not batch-summarize sources without reading them individually.
3. Read each source item one by one and write or rewrite the corresponding wiki page manually.
4. If an existing wiki page looks auto-generated, noisy, or low-quality, overwrite it with a manual curated version.
5. Do not mechanically dump headings or bullet points from the source.
6. Do not create sections like `common methods`, `common tools`, or `best practices` unless the source actually supports a real synthesis.
7. Do not promote a phrase into a concept page merely because it appears in a title.

## How to synthesize instead of templating

When converting a source into wiki content:

1. First decide what the source is really doing: tutorial, case study, opinion, workflow note, benchmark, announcement, troubleshooting log, or resource dump.
2. Identify the few claims or procedures that are genuinely reusable.
3. Separate durable knowledge from transient context, chatter, marketing wording, and title noise.
4. Write concept pages from actual patterns supported by multiple source pages, not from isolated labels.
5. If a source does not contain reusable methodology, say that directly instead of forcing abstract sections.
6. Prefer fewer stronger sections over many weak template sections.

## Recommended operating pattern

Use small batches. The default batch size is 1 source when invoked by the runner.

For each item:

1. Read the source file indicated by the runner.
2. Inspect any relevant local images in the same source directory.
3. Rewrite the corresponding `wiki/03_sources/*.md` page manually.
4. Update only directly affected concept or entity pages.
5. Create or update decision pages only if a reusable conclusion clearly exists.
6. Update `wiki/index.md`.
7. Append progress to `wiki/log.md`.

## Source page standard

Every source page should try to include:

1. what the source is about
2. what is actually reusable from it
3. tools, frameworks, or entities mentioned in substance
4. key facts and conclusions
5. risks, assumptions, or limitations
6. related concepts
7. source path

If a section would be empty or fake, omit it or replace it with a short direct statement.

## Concept page standard

When updating a concept page:

1. Keep the page scoped to durable reusable knowledge.
2. Summarize only patterns that are genuinely supported by the curated sources.
3. Avoid giant catch-all lists copied from source pages.
4. Avoid stock phrases like `common methods` when the underlying sources are heterogeneous or weakly related.
5. If the evidence is thin, keep the page narrow and explicit about limits.

## Index and progress tracking

`wiki/index.md` should track curated pages and durable navigation.

`wiki/log.md` should append entries like:

`## [YYYY-MM-DD] ingest | source-id`

And then briefly list:

1. which source page was written or updated
2. which concept, entity, or decision pages were touched
3. which index pages changed
