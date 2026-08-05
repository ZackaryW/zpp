from __future__ import annotations

import ast
from pathlib import Path


FEATURES = Path(__file__).parents[1] / "features"
ROOTS = ("core", "workflow", "codespaces")


def test_bdd_features_have_only_capability_execution_roots() -> None:
    assert not tuple(FEATURES.glob("*.feature"))
    assert {path.name for path in FEATURES.iterdir() if path.is_dir()} >= {
        *ROOTS,
        "support",
    }
    for name in ROOTS:
        root = FEATURES / name
        assert tuple(root.glob("*.feature")), name
        assert (root / "environment.py").is_file(), name
        assert (root / "steps").is_dir(), name


def test_bdd_bindings_are_small_and_root_owned() -> None:
    for name in ROOTS:
        modules = tuple((FEATURES / name / "steps").glob("*.py"))
        assert modules, name
        for module in modules:
            assert len(module.read_text(encoding="utf-8").splitlines()) <= 500, module


def test_shared_support_registers_no_behave_steps() -> None:
    support = FEATURES / "support"
    modules = tuple(support.glob("*.py"))
    assert modules
    for module in modules:
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            names = {
                decorator.func.id
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
            }
            assert names.isdisjoint({"given", "when", "then", "step"}), module
