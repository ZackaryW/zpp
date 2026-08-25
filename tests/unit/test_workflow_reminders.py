from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from zpp.core.workflows import (
    WorkflowContract,
    WorkflowContractError,
    WorkflowStageContract,
    check_workflow_run,
    delete_workflow_stage,
    insert_workflow_stage,
    modify_workflow_stage,
    record_workflow_result,
    upsert_workflow_stage,
)
from zpp.utils.product_home import ZppHome
from zpp.utils.workflow_reminders import (
    WorkflowReminderError,
    WorkflowReminderRepository,
)

KNOWN_COMPONENTS = frozenset(
    {"zpps-clarify", "zpps-shape-bdd", "zpps-explore", "zpps-wire"}
)


def _contract(name: str = "zpp-new-feature") -> WorkflowContract:
    return WorkflowContract(
        version=1,
        name=name,
        mode="reminder",
        stages=(
            WorkflowStageContract("clarify", "zpps-clarify"),
            WorkflowStageContract("shape-bdd", "zpps-shape-bdd"),
        ),
    )


def _repository(tmp_path: Path) -> WorkflowReminderRepository:
    return WorkflowReminderRepository(
        ZppHome(tmp_path / "home"),
        known_components=KNOWN_COMPONENTS,
    )


def test_start_persists_exact_targets_and_resumes_without_reset(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    root = tmp_path / "repository"

    started = repository.start(_contract(), root=root, change="sample-change")
    advanced = record_workflow_result(
        started.run,
        component="zpps-clarify",
        result="completed",
        accepted_results=frozenset({"completed"}),
    )
    saved = repository.save(started, advanced)
    resumed = repository.start(_contract(), root=root, change="sample-change")

    assert resumed == saved
    assert resumed.run.root == root.resolve()
    assert resumed.run.stages[0].status == "completed"
    assert isinstance(resumed.run.run_id, UUID)
    assert not (tmp_path / "home" / "bundler").exists()


def test_start_preserves_a_different_active_workflow(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    root = tmp_path / "repository"
    repository.start(_contract(), root=root, change="sample-change")

    with pytest.raises(WorkflowReminderError, match="zpp-new-feature"):
        repository.start(
            _contract("zpp-fix-bug"), root=root, change="sample-change"
        )


def test_repository_rejects_a_stale_replacement(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    stored = repository.start(
        _contract(), root=tmp_path / "repository", change="sample-change"
    )
    first = repository.save(
        stored,
        record_workflow_result(
            stored.run,
            component="zpps-clarify",
            result="completed",
            accepted_results=frozenset({"completed"}),
        ),
    )

    with pytest.raises(WorkflowReminderError, match="stale"):
        repository.save(stored, first.run)


def test_stop_removes_only_the_targeted_reminder(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    root = tmp_path / "repository"
    repository.start(_contract(), root=root, change="sample-change")

    assert repository.stop(root=root, change="sample-change") is True
    assert repository.load(root=root, change="sample-change") is None
    assert repository.stop(root=root, change="sample-change") is False
    assert not (tmp_path / "home" / "bundler").exists()


def test_stage_edits_validate_and_preserve_stable_identifiers(tmp_path: Path) -> None:
    run = _repository(tmp_path).start(
        _contract(), root=tmp_path / "repository", change="sample-change"
    ).run

    inserted = insert_workflow_stage(
        run,
        stage_id="custom-explore",
        component="zpps-explore",
        known_components=KNOWN_COMPONENTS,
        before="clarify",
    )
    upserted = upsert_workflow_stage(
        inserted,
        stage_id="custom-explore",
        component="zpps-explore",
        known_components=KNOWN_COMPONENTS,
        before="clarify",
    )
    modified = modify_workflow_stage(
        upserted,
        stage_id="custom-explore",
        component="zpps-wire",
        known_components=KNOWN_COMPONENTS,
    )
    deleted = delete_workflow_stage(modified, stage_id="custom-explore")

    assert [item.id for item in inserted.stages][:2] == [
        "custom-explore",
        "clarify",
    ]
    assert sum(item.id == "custom-explore" for item in upserted.stages) == 1
    assert modified.stages[0].component == "zpps-wire"
    assert all(item.id != "custom-explore" for item in deleted.stages)


def test_invalid_stage_edit_changes_nothing(tmp_path: Path) -> None:
    run = _repository(tmp_path).start(
        _contract(), root=tmp_path / "repository", change="sample-change"
    ).run

    with pytest.raises(WorkflowContractError, match="duplicate"):
        insert_workflow_stage(
            run,
            stage_id="clarify",
            component="zpps-explore",
            known_components=KNOWN_COMPONENTS,
            before="shape-bdd",
        )

    with pytest.raises(WorkflowContractError, match="unknown component"):
        modify_workflow_stage(
            run,
            stage_id="clarify",
            component="zpps-missing",
            known_components=KNOWN_COMPONENTS,
        )


def test_sequence_checks_are_strong_but_non_blocking(tmp_path: Path) -> None:
    run = _repository(tmp_path).start(
        _contract(), root=tmp_path / "repository", change="sample-change"
    ).run

    matching = check_workflow_run(run, component="zpps-clarify")
    warning = check_workflow_run(run, component="zpps-shape-bdd")
    untracked = check_workflow_run(None, component="zpps-explore")
    required = check_workflow_run(
        None,
        component="zpps-clarify",
        workflow="zpp-new-feature",
    )

    assert matching.allowed is True and matching.sequence_match is True
    assert warning.allowed is True and warning.sequence_match is False
    assert warning.expected_stage is not None
    assert warning.expected_stage.id == "clarify"
    assert warning.unfinished_stages == run.stages
    assert untracked.status == "untracked" and untracked.allowed is True
    assert required.status == "workflow-start-required"


def test_only_an_accepted_matching_result_advances(tmp_path: Path) -> None:
    run = _repository(tmp_path).start(
        _contract(), root=tmp_path / "repository", change="sample-change"
    ).run

    unrelated = record_workflow_result(
        run,
        component="zpps-explore",
        result="completed",
        accepted_results=frozenset({"completed"}),
    )
    blocked = record_workflow_result(
        run,
        component="zpps-clarify",
        result="blocked",
        accepted_results=frozenset({"completed"}),
    )
    completed = record_workflow_result(
        run,
        component="zpps-clarify",
        result="completed",
        accepted_results=frozenset({"completed"}),
        observed_bundle=UUID("00000000-0000-0000-0000-000000000001"),
    )

    assert unrelated == run
    assert blocked == run
    assert completed.stages[0].status == "completed"
    assert completed.stages[1].status == "pending"
    assert completed.observed_bundle == UUID(
        "00000000-0000-0000-0000-000000000001"
    )
