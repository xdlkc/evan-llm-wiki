# Generic LLM Wiki Rules

## Goal

This project keeps a Markdown-first wiki that is maintained from raw source material.
The wiki is a durable knowledge layer, not a dump of source files.

## Source Of Truth

Canonical sources live under `raw/`.
By default, ingestable source items are discovered under `raw/_sources/`.

Do not overwrite or rewrite raw sources when updating the wiki.

## Attribution Rule

Prefer a single primary human-readable source file in frontmatter.

1. If `README.md` exists for the source item, list only that file in `sources`.
2. Use auxiliary files such as HTML, JSON, screenshots, or attachments only to verify, disambiguate, or enrich understanding.
3. Do not list auxiliary HTML or JSON files in `sources` unless the project explicitly requires that.

## Knowledge Base Layout

Write durable knowledge into:

1. `wiki/00_overview/`
2. `wiki/01_entities/`
3. `wiki/02_concepts/`
4. `wiki/03_sources/`
5. `wiki/04_projects/`
6. `wiki/05_decisions/`
7. `wiki/index.md`
8. `wiki/log.md`

## Editing Rules

When compiling or updating wiki pages:

1. Prefer updating an existing page over creating a near-duplicate page.
2. Preserve source attribution. Every synthesized claim should be traceable to one or more source files.
3. Summarize, normalize, and merge. Do not copy entire source documents into wiki pages.
4. Keep page names stable and readable.
5. Use Markdown with YAML frontmatter.
6. Include `sources`, `updated_at`, and `confidence` in frontmatter when possible.
7. Mark uncertain or weakly supported statements explicitly.

## Required Reading Behavior

Before writing a wiki page:

1. Read the primary source file directly.
2. If the source directory contains images, screenshots, charts, or diagrams that materially affect interpretation, inspect them as part of the source.
3. Use images to understand workflow, architecture, tables, charts, or UI context, not as decoration.
4. If image content is unreadable or ambiguous, say so explicitly rather than inventing details.

## Source Pages

Each page under `wiki/03_sources/` should capture:

1. what the source is about
2. the actual core methods, arguments, or findings after reading the source
3. tools, frameworks, or entities actually discussed in substance
4. what is genuinely reusable
5. risks, assumptions, limitations, or open questions
6. links back to the primary source file

## Concept Pages

Each page under `wiki/02_concepts/` should represent a durable concept, not a single source title.

Concept pages must not be built by mechanically copying section headers or extracting all bullet labels from source pages.
They should reflect the maintainer's judgment about what durable knowledge is actually present.

## Entity Pages

Entity pages are optional and should only be created when a concept appears repeatedly, such as:

1. people
2. tools
3. libraries
4. products
5. vendors
6. organizations

## Decision Pages

Decision pages record reusable conclusions, tradeoffs, or operational decisions.

## Preferred Workflow

1. Read new or changed source items
2. Inspect relevant images or attachments when needed
3. Extract durable facts and concepts
4. Update source summary pages
5. Merge knowledge into concept or entity pages
6. Refresh indexes or logs if needed

## Anti-Patterns

Do not:

1. treat the wiki as a vector-chunk cache
2. store only embeddings without readable Markdown artifacts
3. replace source links with unsupported synthesis
4. create many tiny redundant pages with overlapping meanings
5. fill concept pages with generic headings like “common methods” unless the source corpus actually supports a meaningful synthesis
6. write obvious template text that could have been produced without reading the source
