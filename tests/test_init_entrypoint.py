from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("test_init_entrypoint.init_llm_wiki", ROOT / "scripts" / "init_llm_wiki.py")
assert SPEC is not None and SPEC.loader is not None
init_llm_wiki = module_from_spec(SPEC)
sys.modules[SPEC.name] = init_llm_wiki
SPEC.loader.exec_module(init_llm_wiki)


def test_init_main_accepts_argv(tmp_path: Path) -> None:
    code = init_llm_wiki.main(["--project-root", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "wiki" / "index.md").exists()
