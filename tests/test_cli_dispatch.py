from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("scripts.llm_wiki_cli", ROOT / "scripts" / "llm_wiki_cli.py")
assert SPEC is not None and SPEC.loader is not None
llm_wiki_cli = module_from_spec(SPEC)
sys.modules[SPEC.name] = llm_wiki_cli
SPEC.loader.exec_module(llm_wiki_cli)


def test_cli_dispatches_init_command(tmp_path: Path) -> None:
    code = llm_wiki_cli.main(["init", "--project-root", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "wiki" / "index.md").exists()
