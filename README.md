# evan-llm-wiki

A generic, agent-maintained LLM wiki toolkit.

This repository extracts the reusable workflow from a real Markdown-first wiki maintenance flow:
- queue one source at a time
- call `codex exec` with a fixed prompt
- let Codex manually read the source and maintain the wiki
- keep queue state, indexes, and logs in plain files

The toolkit is generic. It assumes only that a target project has source material and a wiki directory.

## Key operating rules

- prefer one primary human-readable source in frontmatter
- if `README.md` exists, use only `README.md` in `sources`
- images may be read when they materially affect interpretation
- wiki pages must be synthesized from the source, not templated from titles or headings

## Quick start

1. Initialize a target project:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/init_llm_wiki.py --project-root /path/to/project
```

2. Put source material under one of these defaults:

- `raw/_sources/` as subdirectories containing `README.md`, `index.md`, `content.md`, `raw.md`, `raw.txt`, or `raw_content.html`
- or plain files directly under `raw/_sources/`

3. Rebuild the queue:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --rebuild-queue
```

4. Dry-run the next item:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --dry-run
```

5. Process one item:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-once
```

6. Process all pending items:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-all
```
