from collections.abc import Callable
from pathlib import Path

import pathspec

from unskein import pipeline
from unskein.config import AnalysisConfig
from unskein.graph.findings import FindingKind
from unskein.graph.metrics import analyze
from unskein.parsers.models import ParseResult, WarningCode
from unskein.parsers.python_parser import PythonAdapter

MakeProject = Callable[[dict[str, str]], Path]
EMPTY_SPEC = pathspec.PathSpec([])
Edges = set[tuple[str, str, bool]]
# A manifest whose package is found by convention: everything outside ``app/`` is unpackaged.
APP_MANIFEST = '[project]\nname = "app"\n'


def parse(root: Path, config: AnalysisConfig | None = None) -> ParseResult:
    """Parse a whole project the way a scan does: scripts are known only after every file."""
    adapter = PythonAdapter(config)
    return adapter.parse(sorted(adapter.discover_files(root, EMPTY_SPEC)), root)


def as_edges(result: ParseResult) -> Edges:
    """Return the (source, target, external) edges of a parse result."""
    return {(e.source, e.target, e.is_external) for m in result.modules for e in m.imports}


def edges(root: Path, config: AnalysisConfig | None = None) -> Edges:
    """Parse a project and return its (source, target, external) edges."""
    return as_edges(parse(root, config))


def test_script_imports_a_sibling_file_in_a_directory_without_init(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "tools/skripte/run.py": "import zweifel\nfrom regeln import VERSION\n",
            "tools/skripte/zweifel.py": "",
            "tools/skripte/regeln.py": "VERSION = 1\n",
        }
    )

    found = edges(root)

    assert ("tools.skripte.run", "tools.skripte.zweifel", False) in found
    assert ("tools.skripte.run", "tools.skripte.regeln", False) in found


def test_sibling_package_with_submodule_resolves(make_project: MakeProject) -> None:
    root = make_project(
        {
            "tools/run.py": "from helpers.io import read\n",
            "tools/helpers/__init__.py": "",
            "tools/helpers/io.py": "def read(): ...\n",
        }
    )

    assert ("tools.run", "tools.helpers.io", False) in edges(root)


def test_import_without_a_sibling_stays_external(make_project: MakeProject) -> None:
    root = make_project({"tools/run.py": "import requests\n", "tools/other.py": ""})

    assert ("tools.run", "requests", True) in edges(root)


def test_module_of_a_regular_package_does_not_import_siblings_absolutely(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "pkg/__init__.py": "",
            "pkg/run.py": "import helper\n",
            "pkg/helper.py": "",
        }
    )

    assert ("pkg.run", "helper", True) in edges(root)


def test_import_that_already_resolves_in_the_project_is_left_alone(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "core/__init__.py": "",
            "tools/run.py": "import core\n",
            "tools/core.py": "",
        }
    )

    assert ("tools.run", "core", False) in edges(root)


def test_script_resolves_a_sibling_and_a_package_alias_in_the_same_project(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "verwaltung/__init__.py": "",
            "verwaltung/admin_web/__init__.py": "",
            "verwaltung/admin_web/api.py": "",
            "tools/run.py": "import helper\nimport admin_web.api\nfrom admin_web import api\n",
            "tools/helper.py": "",
        }
    )
    config = AnalysisConfig(module_aliases={"admin_web": "verwaltung.admin_web"})

    found = edges(root, config)

    assert ("tools.run", "tools.helper", False) in found
    assert ("tools.run", "verwaltung.admin_web.api", False) in found
    assert not {target for _, target, _ in found if target.startswith("admin_web")}


def test_module_that_other_code_imports_is_not_a_script(make_project: MakeProject) -> None:
    root = make_project(
        {
            "app/__init__.py": "",
            "app/main.py": "import tools.run\n",
            "tools/run.py": "import helper\n",
            "tools/helper.py": "",
        }
    )

    found = edges(root)

    assert ("tools.run", "helper", True) in found
    assert not {source for source, target, _ in found if target == "tools.helper"}


def test_lazy_import_of_a_module_is_enough_to_make_it_not_a_script(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "app/__init__.py": "",
            "app/main.py": "def load():\n    from tools import run\n",
            "tools/run.py": "import helper\n",
            "tools/helper.py": "",
        }
    )

    assert ("tools.run", "helper", True) in edges(root)


def test_module_named_like_a_dependency_stays_external_when_its_importer_is_imported(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "app/__init__.py": "",
            "app/main.py": "from tools.run import main\n",
            "tools/run.py": "import yaml\ndef main(): ...\n",
            "tools/yaml.py": "",
        }
    )

    assert ("tools.run", "yaml", True) in edges(root)


def test_sibling_imported_by_a_script_resolves_its_own_siblings(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "tools/run.py": "import helper\n",
            "tools/helper.py": "import util\n",
            "tools/util.py": "",
        }
    )

    found = edges(root)

    assert ("tools.run", "tools.helper", False) in found
    assert ("tools.helper", "tools.util", False) in found


def test_module_of_a_shipped_namespace_package_is_not_a_script(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "pyproject.toml": '[project]\nname = "firma-werkzeug"\n'
            '[tool.setuptools]\npackages = ["firma.werkzeug"]\n',
            "firma/werkzeug/run.py": "import yaml\n",
            "firma/werkzeug/yaml.py": "",
        }
    )

    assert ("firma.werkzeug.run", "yaml", True) in edges(root)


def test_unpackaged_script_next_to_a_shipped_package_resolves_siblings(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "pyproject.toml": APP_MANIFEST,
            "app/__init__.py": "",
            "tools/run.py": "import helper\nimport app\n",
            "tools/helper.py": "",
        }
    )

    found = edges(root)

    assert ("tools.run", "tools.helper", False) in found
    assert ("tools.run", "app", False) in found


def test_import_of_a_submodule_a_sibling_file_lacks_points_at_the_sibling(
    make_project: MakeProject,
) -> None:
    root = make_project(
        {
            "pyproject.toml": APP_MANIFEST,
            "app/__init__.py": "",
            "tools/run.py": "import helper.missing\n",
            "tools/helper.py": "",
        }
    )

    result = parse(root)

    (edge,) = [e for m in result.modules for e in m.imports if e.source == "tools.run"]
    assert (edge.target, edge.is_external) == ("tools.helper", False)
    assert edge.requested == "tools.helper.missing"
    (warning,) = [w for w in result.warnings if w.code is WarningCode.UNRESOLVED_IMPORT]
    assert warning.detail == "tools.helper.missing -> tools.helper"
    assert "tools.helper.missing" not in {m.name for m in result.modules}
    findings = analyze(PythonAdapter().resolve_indirection(result)).findings
    assert not [f for f in findings if f.kind is FindingKind.MISSING_MODULE]


def test_parallel_parsing_resolves_the_same_siblings(make_project: MakeProject) -> None:
    root = make_project(
        {
            "app/__init__.py": "",
            "app/main.py": "import tools.imported\n",
            "tools/run.py": "import helper\n",
            "tools/imported.py": "import helper\n",
            "tools/helper.py": "",
        }
    )
    config = AnalysisConfig(parallel_threshold=1)
    adapter = PythonAdapter(config)
    files = sorted(adapter.discover_files(root, EMPTY_SPEC))

    parallel = as_edges(pipeline.parse_all(files, adapter, root, config))

    assert parallel == edges(root)
    assert ("tools.run", "tools.helper", False) in parallel
    assert ("tools.imported", "helper", True) in parallel
