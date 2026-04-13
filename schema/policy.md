# LLM Wiki Policy

## Metadata

Every wiki page should try to include frontmatter:

```yaml
---
id: source/example
kind: source|concept|entity|project|decision|overview
updated_at: 2026-04-14
sources:
  - raw/_sources/example/README.md
confidence: medium
---
```

## Source attribution

1. Prefer one primary human-readable source in `sources`.
2. If `README.md` exists, use only that path in `sources`.
3. Auxiliary HTML, JSON, screenshots, and attachments may be read for context, but should usually not be listed in `sources`.

## Body structure

Preferred order:

1. Definition or summary
2. Core points
3. Evidence and traceability
4. Risks or limitations
5. Related pages
6. Open questions

Do not keep placeholder sections that add no real information.

## Traceability

Every non-trivial synthesis should be traceable to listed source files.

## Image handling

If local images materially affect interpretation, inspect them before writing.
Do not invent details from blurry or ambiguous images.
