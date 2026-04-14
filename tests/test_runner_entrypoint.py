from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("test_runner_entrypoint.llm_wiki_runner", ROOT / "scripts" / "llm_wiki_runner.py")
assert SPEC is not None and SPEC.loader is not None
llm_wiki_runner = module_from_spec(SPEC)
sys.modules[SPEC.name] = llm_wiki_runner
SPEC.loader.exec_module(llm_wiki_runner)


def test_runner_main_accepts_argv(tmp_path: Path) -> None:
    code = llm_wiki_runner.main(["--project-root", str(tmp_path), "--rebuild-queue"])
    assert code == 0
    assert (tmp_path / "wiki" / "_system" / "manual_queue.json").exists()
