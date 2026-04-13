# Usage

## 1. Initialize a target project

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/init_llm_wiki.py --project-root /path/to/project
```

## 2. Put source material under `raw/_sources/`

Supported by default:

- one directory per source, with a primary file like `README.md`, `index.md`, `content.md`, `raw.md`, `raw.txt`, or `raw_content.html`
- or plain `.md`, `.txt`, `.html`, `.htm` files directly under `raw/_sources/`

If a source directory also contains screenshots, charts, or diagrams, the model should inspect them when they materially affect interpretation.

## 3. Rebuild queue

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --rebuild-queue
```

## 4. Run Codex one source at a time

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-once
```

## 5. Run continuously

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-all
```

## 6. Useful controls

Dry-run next item:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --dry-run
```

Retry failed items:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --retry-failed
```

Process one specific source:

```bash
python /Users/lkc/Code/evan-llm-wiki/scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --only-source-id example-source
```

## Writing expectations

- `sources` should usually contain only the primary readable source file
- if `README.md` exists, prefer only `README.md`
- concept pages should reflect real synthesis, not title extraction or heading extraction
- if a source has little reusable methodology, say that plainly instead of forcing a template
