"""Bootstrap one neutral audit project and clone fresh workflow workspaces."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import NoReturn


def _fail(message: str) -> NoReturn:
    raise SystemExit(message)


def _run(arguments: list[str], *, cwd: Path) -> str:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        _fail(
            f"command failed ({result.returncode}): {arguments!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def _require_empty(path: Path, *, label: str) -> Path:
    selected = path.resolve()
    if selected.exists() and any(selected.iterdir()):
        _fail(f"{label} must be absent or empty: {selected}")
    selected.mkdir(parents=True, exist_ok=True)
    return selected


def _assert_scope(repository: Path) -> None:
    expected = repository.resolve()
    git_root = Path(
        _run(["git", "rev-parse", "--show-toplevel"], cwd=expected).strip()
    ).resolve()
    context = json.loads(_run(["openspec", "context", "--json"], cwd=expected))
    openspec_root = Path(context["root"]["path"]).resolve()
    if git_root != expected or openspec_root != expected:
        _fail(
            "mock project identity mismatch: "
            f"expected={expected}, git={git_root}, openspec={openspec_root}"
        )


def _head(repository: Path) -> str:
    return _run(["git", "rev-parse", "HEAD"], cwd=repository).strip()


def _require_clean(repository: Path, *, label: str) -> None:
    status = _run(["git", "status", "--porcelain=v1"], cwd=repository)
    if status:
        _fail(f"{label} must be clean: {status}")


def bootstrap(base: Path) -> dict[str, object]:
    root = _require_empty(base, label="base")
    _run(["git", "init", "--quiet", str(root)], cwd=root.parent)
    _run(
        [
            "openspec",
            "init",
            str(root),
            "--tools",
            "none",
            "--no-animation",
        ],
        cwd=root.parent,
    )
    _assert_scope(root)
    _run(["git", "add", "--all"], cwd=root)
    _run(
        [
            "git",
            "-c",
            "user.name=ZPP Workflow Audit",
            "-c",
            "user.email=audit@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "chore: bootstrap workflow audit fixture",
        ],
        cwd=root,
    )
    _require_clean(root, label="base")
    return {
        "version": 1,
        "operation": "bootstrap",
        "root": str(root),
        "head": _head(root),
    }


def clone(base: Path, destination: Path, product_home: Path) -> dict[str, object]:
    source = base.resolve()
    if not source.is_dir():
        _fail(f"base repository does not exist: {source}")
    _assert_scope(source)
    _require_clean(source, label="base")
    base_head = _head(source)

    target = destination.resolve()
    if target.exists() and any(target.iterdir()):
        _fail(f"destination must be absent or empty: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    _run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(source), str(target)],
        cwd=target.parent,
    )
    home = _require_empty(product_home, label="product home")
    _assert_scope(target)
    _require_clean(target, label="clone")
    if _head(target) != base_head:
        _fail("clone does not match the immutable base revision")
    return {
        "version": 1,
        "operation": "clone",
        "base": str(source),
        "base_head": base_head,
        "root": str(target),
        "product_home": str(home),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="operation", required=True)
    bootstrap_parser = commands.add_parser("bootstrap")
    bootstrap_parser.add_argument("--base", type=Path, required=True)
    clone_parser = commands.add_parser("clone")
    clone_parser.add_argument("--base", type=Path, required=True)
    clone_parser.add_argument("--destination", type=Path, required=True)
    clone_parser.add_argument("--product-home", type=Path, required=True)
    return parser


def main() -> None:
    arguments = _parser().parse_args()
    if arguments.operation == "bootstrap":
        result = bootstrap(arguments.base)
    else:
        result = clone(arguments.base, arguments.destination, arguments.product_home)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
