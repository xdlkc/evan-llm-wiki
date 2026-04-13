# LLM Wiki Workflows

## Ingest

1. Add or update raw source files under `raw/_sources/`
2. Rebuild the queue
3. Run the manual runner one item at a time or continuously
4. For each source, read the main text and inspect relevant local images if needed
5. Review changed wiki pages if needed

## Query

1. Start from `wiki/index.md`
2. Traverse relevant source, concept, entity, project, or decision pages
3. Prefer reusing existing wiki pages over rereading raw sources

## Lint

1. Find orphaned pages
2. Find stale or low-confidence pages
3. Find duplicated concept pages
4. Find concept pages that contain template language unsupported by evidence
5. Produce repair tasks in `wiki/05_decisions/`
