"""Public-system subjects for full mock workflow audits."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.artifacts import packaged_companion_skills, packaged_workflow_contracts
from zpp.cli import app


@dataclass(frozen=True, slots=True)
class AuditAssignment:
    workflow: str
    contract_path: Path
    playbook_path: Path
    component_paths: tuple[tuple[Path, Path], ...]


@dataclass(frozen=True, slots=True)
class Gap:
    kind: str
    transition: str
    observed: str
    closeout: str


@dataclass(frozen=True, slots=True)
class MockResult:
    workflow: str
    revision: int
    repository: Path
    product_home: Path
    change: str
    declared_stages: tuple[tuple[str, str], ...]
    recorded_stages: tuple[tuple[str, str], ...]
    branches: tuple[str, ...]
    gaps: tuple[Gap, ...]
    archive_path: Path
    operations: tuple[str, ...]


class Audit:
    def __init__(self) -> None:
        self.source = Path(__file__).resolve().parents[2]
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.workflows = packaged_workflow_contracts()
        self.audit_skill = next(
            skill
            for skill in packaged_companion_skills()
            if skill.name == "zpp-audit-workflows"
        )
        self.assignments = tuple(
            self._assignment(workflow) for workflow in self.workflows
        )

    def close(self) -> None:
        self._temporary.cleanup()

    def _assignment(self, workflow) -> AuditAssignment:
        contracts = self.source / "src/zpp/artifacts/workflow_contracts"
        skills = self.source / "src/zpp/artifacts/skills/workflow"
        return AuditAssignment(
            workflow=workflow.name,
            contract_path=contracts / "workflows" / f"{workflow.name}.json",
            playbook_path=skills / workflow.name / "SKILL.md",
            component_paths=tuple(
                (
                    contracts / "components" / f"{stage.component}.json",
                    skills / stage.component / "SKILL.md",
                )
                for stage in workflow.stages
            ),
        )

    def _run(self, arguments: list[str], *, cwd: Path | None = None) -> str:
        result = subprocess.run(
            arguments,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"command failed: {arguments!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        return result.stdout

    def _workflow(
        self,
        product_home: Path,
        *arguments: str,
    ) -> dict[str, object]:
        result = CliRunner().invoke(
            app,
            ["--path", str(product_home), "workflow", "run", *arguments],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.stdout)
        assert isinstance(payload, dict), payload
        return payload

    def _write_complete_change(self, repository: Path, change: str) -> None:
        root = repository / "openspec/changes" / change
        (root / "specs/mock-workflow").mkdir(parents=True)
        (root / "proposal.md").write_text(
            """## Why

Exercise one complete workflow in disposable state.

## What Changes

- Add a synthetic workflow marker.

## Capabilities

### New Capabilities

- `mock-workflow`: Disposable workflow closeout behavior.

### Modified Capabilities

None.

## Impact

Temporary audit repository only.
""",
            encoding="utf-8",
            newline="\n",
        )
        (root / "specs/mock-workflow/spec.md").write_text(
            """## Purpose

Exercise a complete ZPP workflow inside a disposable audit repository.

## ADDED Requirements

### Requirement: Close a synthetic workflow
The audit fixture SHALL reach validated and archived change state.

#### Scenario: Close the change
- **WHEN** every declared workflow stage returns an accepted mock result
- **THEN** the synthetic change is validated and archived locally
""",
            encoding="utf-8",
            newline="\n",
        )
        (root / "design.md").write_text(
            """## Context

This disposable change exercises orchestration only.

## Goals / Non-Goals

**Goals:** close the mock workflow.

**Non-Goals:** implement a durable product.

## Decisions

Use one minimal marker capability so OpenSpec lifecycle commands are real.

## Risks / Trade-offs

- Mock product behavior is intentionally shallow.
""",
            encoding="utf-8",
            newline="\n",
        )
        (root / "tasks.md").write_text(
            """## 1. Mock workflow

- [x] 1.1 Exercise every declared stage and branch.
- [x] 1.2 Validate and archive the synthetic change.
""",
            encoding="utf-8",
            newline="\n",
        )

    def run_mock(
        self,
        assignment: AuditAssignment,
        *,
        revision: int = 1,
    ) -> MockResult:
        base = self.base / f"{assignment.workflow}-r{revision}"
        repository = base / "repository"
        product_home = base / "product-home"
        repository.mkdir(parents=True)
        assert not tuple(repository.iterdir())

        self._run(["git", "init", "--quiet", str(repository)])
        self._run(
            [
                "openspec",
                "init",
                str(repository),
                "--tools",
                "none",
                "--no-animation",
            ]
        )
        assert (repository / ".git").is_dir()
        assert (repository / "openspec").is_dir()

        change = f"audit-{assignment.workflow}-r{revision}"
        self._run(["openspec", "new", "change", change], cwd=repository)
        initial = json.loads(
            self._run(
                ["openspec", "status", "--change", change, "--json"],
                cwd=repository,
            )
        )
        assert initial["isComplete"] is False
        gaps = (
            Gap(
                "fixture-gap",
                "planning",
                "fresh OpenSpec change has incomplete planning artifacts",
                "closed-in-fixture",
            ),
            Gap(
                "fixture-gap",
                "archive",
                "OpenSpec archive requires explicit non-interactive confirmation",
                "closed-in-fixture",
            ),
        )
        self._write_complete_change(repository, change)
        complete = json.loads(
            self._run(
                ["openspec", "status", "--change", change, "--json"],
                cwd=repository,
            )
        )
        assert complete["isComplete"] is True
        self._run(
            ["openspec", "validate", change, "--strict", "--json"],
            cwd=repository,
        )

        started = self._workflow(
            product_home,
            "start",
            assignment.workflow,
            "--root",
            str(repository),
            "--change",
            change,
        )
        declared = tuple(
            (stage["id"], stage["component"]) for stage in started["stages"]
        )
        recorded: list[tuple[str, str]] = []
        for stage_id, component in declared:
            checked = self._workflow(
                product_home,
                "check",
                "--root",
                str(repository),
                "--change",
                change,
                "--workflow",
                assignment.workflow,
                "--component",
                component,
            )
            assert checked["sequence_match"] is True, checked
            self._workflow(
                product_home,
                "record",
                "--root",
                str(repository),
                "--change",
                change,
                "--component",
                component,
                "--result",
                "completed",
            )
            recorded.append((stage_id, component))

        final_status = self._workflow(
            product_home,
            "status",
            "--root",
            str(repository),
            "--change",
            change,
        )
        assert final_status["next_stage"] is None, final_status
        archive = json.loads(
            self._run(
                ["openspec", "archive", change, "--json", "--yes"],
                cwd=repository,
            )
        )["archive"]
        archive_path = Path(archive["path"])
        assert archive_path.is_dir(), archive_path
        self._workflow(
            product_home,
            "stop",
            "--root",
            str(repository),
            "--change",
            change,
        )

        return MockResult(
            assignment.workflow,
            revision,
            repository,
            product_home,
            change,
            declared,
            tuple(recorded),
            (
                "planning-operation",
                "sync",
                "repository-verification",
                "change-verification",
                "finalization",
                "archive",
            ),
            gaps,
            archive_path,
            (
                "git-init",
                "openspec-init",
                "change-create",
                "planning-gap",
                "planning-closeout",
                "strict-validation",
                "stage-check-and-record",
                "archive",
                "reminder-stop",
            ),
        )
