"""Public-system subjects for the packaged workflow audit skill."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.artifacts import (
    packaged_companion_skills,
    packaged_component_contracts,
    packaged_workflow_contracts,
)
from zpp.cli import app


@dataclass(frozen=True, slots=True)
class AuditAssignment:
    workflow: str
    contract_path: Path
    playbook_path: Path
    component_paths: tuple[tuple[Path, Path], ...]


@dataclass(frozen=True, slots=True)
class SimulationEvidence:
    workflow: str
    product_home: Path
    operations: tuple[str, ...]


class Audit:
    def __init__(self) -> None:
        self.repository = Path(__file__).resolve().parents[2]
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.workflows = packaged_workflow_contracts()
        self.components = {
            component.name: component for component in packaged_component_contracts()
        }
        self.audit_skill = next(
            skill
            for skill in packaged_companion_skills()
            if skill.name == "zpp-audit-workflows"
        )
        self.assignments = tuple(self._assignment(workflow) for workflow in self.workflows)

    def close(self) -> None:
        self._temporary.cleanup()

    def _assignment(self, workflow) -> AuditAssignment:
        component_paths = tuple(
            (
                self.repository
                / "src"
                / "zpp"
                / "artifacts"
                / "workflow_contracts"
                / "components"
                / f"{stage.component}.json",
                self.repository
                / "src"
                / "zpp"
                / "artifacts"
                / "skills"
                / "workflow"
                / stage.component
                / "SKILL.md",
            )
            for stage in workflow.stages
        )
        return AuditAssignment(
            workflow=workflow.name,
            contract_path=self.repository
            / "src"
            / "zpp"
            / "artifacts"
            / "workflow_contracts"
            / "workflows"
            / f"{workflow.name}.json",
            playbook_path=self.repository
            / "src"
            / "zpp"
            / "artifacts"
            / "skills"
            / "workflow"
            / workflow.name
            / "SKILL.md",
            component_paths=component_paths,
        )

    def simulate(self, assignment: AuditAssignment, *, revision: int = 1) -> SimulationEvidence:
        product_home = self.base / f"{assignment.workflow}-{revision}"
        repository = self.base / f"repository-{assignment.workflow}-{revision}"
        repository.mkdir()
        change = f"audit-{assignment.workflow}-{revision}"
        runner = CliRunner()

        def invoke(*arguments: str) -> dict:
            result = runner.invoke(
                app,
                ["--path", str(product_home), "workflow", "run", *arguments],
                catch_exceptions=False,
            )
            assert result.exit_code == 0, result.output
            payload = json.loads(result.stdout)
            assert isinstance(payload, dict), payload
            return payload

        started = invoke(
            "start",
            assignment.workflow,
            "--root",
            str(repository),
            "--change",
            change,
        )
        first = started["stages"][0]
        invoke(
            "check",
            "--root",
            str(repository),
            "--change",
            change,
            "--workflow",
            assignment.workflow,
            "--component",
            first["component"],
        )
        invoke(
            "check",
            "--root",
            str(repository),
            "--change",
            change,
            "--workflow",
            assignment.workflow,
            "--component",
            started["stages"][1]["component"],
        )
        invoke(
            "stage",
            "upsert",
            "--root",
            str(repository),
            "--change",
            change,
            "--id",
            "audit-explore",
            "--component",
            "zpps-explore",
            "--before",
            first["id"],
        )
        invoke(
            "stage",
            "delete",
            "--root",
            str(repository),
            "--change",
            change,
            "--id",
            "audit-explore",
        )
        invoke(
            "record",
            "--root",
            str(repository),
            "--change",
            change,
            "--component",
            first["component"],
            "--result",
            "completed",
        )
        resumed = invoke(
            "start",
            assignment.workflow,
            "--root",
            str(repository),
            "--change",
            change,
        )
        assert resumed["stages"][0]["status"] == "completed", resumed
        return SimulationEvidence(
            assignment.workflow,
            product_home,
            ("start", "check-match", "check-warning", "upsert", "delete", "record", "resume"),
        )

    def compare(self) -> dict[str, dict[str, object]]:
        return {
            assignment.workflow: {
                "evidence": (
                    assignment.contract_path,
                    assignment.playbook_path,
                    *(
                        path
                        for pair in assignment.component_paths
                        for path in pair
                    ),
                ),
                "findings": (),
                "checks": {"contract": "passed", "simulation": "not-run"},
            }
            for assignment in self.assignments
        }
