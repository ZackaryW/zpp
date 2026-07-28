import json
import subprocess
from pathlib import Path

import pytest

from zpp.core import governance, isolation, sidecar, worksets


def _git(path, *args):
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)


def _init_git_repo(path, remote=None):
    path.mkdir()
    _git(path, "init")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")
    (path / "README.md").write_text("fixture\n")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "initial")
    if remote:
        _git(path, "remote", "add", "origin", remote)


def test_local_root_is_self_governed(tmp_path, fake_openspec):
    repo = tmp_path / "solo"
    (repo / "openspec").mkdir(parents=True)
    result = governance.resolve(repo)
    assert result["mode"] == "self-governed" and result["rule"] == 1


def _set_profiles(name, profiles):
    side = sidecar.load(name)
    side["profiles"] = profiles
    sidecar.save(name, side)


def test_committed_binding_beats_profile(tmp_path, fake_openspec, workspace_file):
    fake_openspec["stores"] = {"store-a": str(tmp_path / "sa"), "store-b": str(tmp_path / "sb")}
    repo = tmp_path / "repo-a"
    (repo / "zpp.toml").write_text('[governance]\nstore = "store-a"\n')
    worksets.do_import(workspace_file)
    _set_profiles("demo", {"default": {"governance": {"store": "store-b"}}})  # profile disagrees
    result = governance.resolve(repo)
    assert result["rule"] == 2 and result["store"] == "store-a"


def test_profile_binding_is_rule_three(tmp_path, fake_openspec, workspace_file):
    fake_openspec["stores"]["gov"] = str(tmp_path / "gov")
    worksets.do_import(workspace_file)
    _set_profiles("demo", {"default": {"governance": {"store": "gov"}}})
    result = governance.resolve(tmp_path / "repo-b")
    assert result["rule"] == 3 and result["binding"] == "profile"
    assert result["workset"] == "demo" and result["profile"] == "default"


def test_ungoverned_is_explicit_and_dangling_store_warns(tmp_path, fake_openspec):
    assert governance.resolve(tmp_path / "nowhere")["mode"] == "ungoverned"
    repo = tmp_path / "dangling"
    repo.mkdir()
    (repo / "zpp.toml").write_text('[governance]\nstore = "gone"\n')
    result = governance.resolve(repo)
    assert result["store"] == "gone" and any("dangling" in w for w in result["warnings"])


def test_config_scalar_override_and_list_union(tmp_path, fake_openspec):
    store_root = tmp_path / "gov-store"
    store_root.mkdir()
    (store_root / "zpp.toml").write_text(
        '[profiles.default.zmem]\nmode = "present"\n'
        '[profiles.default.agent]\nshards = ["base"]\n'
    )
    fake_openspec["stores"]["gov"] = str(store_root)
    repo = tmp_path / "governed"
    repo.mkdir()
    (repo / "zpp.toml").write_text(
        '[governance]\nstore = "gov"\n[zmem]\nmode = "apply"\n[agent]\nshards = ["extra"]\n'
    )
    result = governance.resolve_config(repo)
    assert result["effective"]["zmem"]["mode"] == "apply"
    assert result["effective"]["agent"]["shards"] == ["base", "extra"]
    assert result["origins"]["zmem.mode"] == "repo"


def test_self_governed_repo_is_its_own_store_layer(tmp_path, fake_openspec):
    repo = tmp_path / "solo"
    (repo / "openspec").mkdir(parents=True)
    (repo / "zpp.toml").write_text(
        '[zmem]\nmode = "apply"\n[profiles.default.zmem]\nmode = "present"\n')
    result = governance.resolve_config(repo)
    assert result["mode"]["mode"] == "self-governed"
    assert result["effective"]["zmem"]["mode"] == "apply"


def _scoped_repo(tmp_path):
    repo = tmp_path / "scoped-repo"
    (repo / "openspec").mkdir(parents=True)
    (repo / "zpp.toml").write_text(
        '[tdd]\nstack = "rust"\n'
        '[traits]\napply = ["root"]\n'
        '[doctor]\nexclude = ["node"]\n'
        '[doctor.settings]\nstrict = false\n'
    )
    return repo


def test_root_only_resolution_keeps_the_existing_source_shape(tmp_path, fake_openspec):
    repo = _scoped_repo(tmp_path)

    result = governance.resolve_config(repo)

    assert set(result) == {"mode", "effective", "origins", "layers"}
    assert result["layers"] == {
        "store": {},
        "workset": {},
        "repo": {
            "tdd": {"stack": "rust"},
            "traits": {"apply": ["root"]},
            "doctor": {
                "exclude": ["node"],
                "settings": {"strict": False},
            },
        },
    }
    assert result["origins"] == {
        "tdd.stack": "repo",
        "traits.apply": "repo",
        "doctor.exclude": "repo",
        "doctor.settings.strict": "repo",
    }


def test_scopes_merge_root_to_target_with_ordered_canonical_sources(
    tmp_path, fake_openspec
):
    repo = _scoped_repo(tmp_path)
    sdk = repo / "sdk"
    python = sdk / "python"
    target = python / "src"
    target.mkdir(parents=True)
    (sdk / "zpp.toml").write_text(
        '[traits]\napply = ["sdk", "root"]\n'
        '[doctor]\nexclude = ["python"]\n'
        '[doctor.settings]\ncolor = "always"\n'
    )
    (python / "zpp.toml").write_text(
        '[tdd]\nstack = "python"\n'
        '[traits]\napply = ["python"]\n'
        '[doctor.settings]\nstrict = true\n'
    )
    sdk_source = str((sdk / "zpp.toml").resolve())
    python_source = str((python / "zpp.toml").resolve())

    result = governance.resolve_config(target)

    assert result["effective"] == {
        "tdd": {"stack": "python"},
        "traits": {"apply": ["root", "sdk", "python"]},
        "doctor": {
            "exclude": ["node", "python"],
            "settings": {"strict": True, "color": "always"},
        },
    }
    assert result["scoped_layers"] == [
        {
            "source": sdk_source,
            "config": {
                "traits": {"apply": ["sdk", "root"]},
                "doctor": {
                    "exclude": ["python"],
                    "settings": {"color": "always"},
                },
            },
        },
        {
            "source": python_source,
            "config": {
                "tdd": {"stack": "python"},
                "traits": {"apply": ["python"]},
                "doctor": {"settings": {"strict": True}},
            },
        },
    ]
    assert result["origins"]["tdd.stack"] == python_source
    assert result["origins"]["doctor.settings.strict"] == python_source
    assert result["origins"]["doctor.settings.color"] == sdk_source
    assert result["origins"]["traits.apply"].endswith(python_source)


def test_file_target_uses_its_parent_scope(tmp_path, fake_openspec):
    repo = _scoped_repo(tmp_path)
    package = repo / "sdk" / "python"
    package.mkdir(parents=True)
    source_file = package / "client.py"
    source_file.write_text("pass\n")
    (package / "zpp.toml").write_text('[tdd]\nstack = "python"\n')

    result = governance.resolve_config(source_file)

    assert result["effective"]["tdd"]["stack"] == "python"
    assert result["scoped_layers"][0]["source"] == str(
        (package / "zpp.toml").resolve()
    )


@pytest.mark.parametrize(
    ("content", "sections"),
    [
        ('[governance]\nstore = "other"\n', ("[governance]",)),
        ('[profiles.default]\nname = "nested"\n', ("[profiles]",)),
        (
            '[governance]\nstore = "other"\n[profiles.default]\nname = "nested"\n',
            ("[governance]", "[profiles]"),
        ),
    ],
)
def test_nested_authority_sections_name_file_and_every_prohibited_section(
    tmp_path, fake_openspec, content, sections
):
    repo = _scoped_repo(tmp_path)
    scope = repo / "sdk" / "python"
    scope.mkdir(parents=True)
    config = scope / "zpp.toml"
    config.write_text(content)

    with pytest.raises(governance.ScopedConfigError) as raised:
        governance.resolve_config(scope)

    assert str(config.resolve()) in str(raised.value)
    for section in sections:
        assert section in str(raised.value)


def test_nested_binding_does_not_replace_the_established_git_root_binding(
    tmp_path, fake_openspec, monkeypatch
):
    repo = tmp_path / "external-repo"
    _init_git_repo(repo)
    fake_openspec["stores"] = {
        "root-store": str(tmp_path / "root-store"),
        "nested-store": str(tmp_path / "nested-store"),
    }
    (repo / "zpp.toml").write_text('[governance]\nstore = "root-store"\n')
    scope = repo / "sdk" / "python"
    scope.mkdir(parents=True)
    (scope / "zpp.toml").write_text('[governance]\nstore = "nested-store"\n')
    monkeypatch.setattr(governance.adapter, "find_openspec_root", lambda path: None)

    resolved = governance.resolve(scope)

    assert resolved["mode"] == "externally-governed"
    assert resolved["store"] == "root-store"
    assert resolved["root"] == str(repo.resolve())


def test_ungoverned_git_descendant_inherits_ordinary_root_config(
    tmp_path, fake_openspec
):
    repo = tmp_path / "ungoverned-repo"
    _init_git_repo(repo)
    (repo / "zpp.toml").write_text('[tdd]\nstack = "rust"\n')
    target = repo / "crates" / "core"
    target.mkdir(parents=True)

    resolved = governance.resolve_config(target)

    assert resolved["mode"]["mode"] == "ungoverned"
    assert resolved["effective"]["tdd"]["stack"] == "rust"
    assert resolved["origins"]["tdd.stack"] == "repo"
    assert "scoped_layers" not in resolved


def test_root_and_sibling_do_not_inherit_child_scope(tmp_path, fake_openspec):
    repo = _scoped_repo(tmp_path)
    python = repo / "sdk" / "python"
    sibling = repo / "crates" / "core"
    python.mkdir(parents=True)
    sibling.mkdir(parents=True)
    (python / "zpp.toml").write_text(
        '[tdd]\nstack = "python"\n[bdd]\nstack = "python"\n'
    )

    root_result = governance.resolve_config(repo)
    python_result = governance.resolve_config(python)
    sibling_result = governance.resolve_config(sibling)

    assert root_result["effective"]["tdd"]["stack"] == "rust"
    assert "bdd" not in root_result["effective"]
    assert python_result["effective"]["tdd"]["stack"] == "python"
    assert python_result["effective"]["bdd"]["stack"] == "python"
    assert sibling_result["effective"]["tdd"]["stack"] == "rust"
    assert "bdd" not in sibling_result["effective"]
    for key in ("mode", "rule", "store", "root", "isolation"):
        assert python_result["mode"].get(key) == root_result["mode"].get(key)
        assert sibling_result["mode"].get(key) == root_result["mode"].get(key)


def test_canonical_parent_traversal_cannot_borrow_scopes_across_root(
    tmp_path, fake_openspec
):
    repo = _scoped_repo(tmp_path)
    python = repo / "sdk" / "python"
    python.mkdir(parents=True)
    (python / "zpp.toml").write_text('[tdd]\nstack = "python"\n')
    outside = tmp_path / "outside"
    (outside / "openspec").mkdir(parents=True)
    (outside / "zpp.toml").write_text('[tdd]\nstack = "typescript"\n')

    escaped = governance.resolve_config(python / ".." / ".." / ".." / "outside")

    assert escaped["mode"]["root"] == str(outside.resolve())
    assert escaped["effective"]["tdd"]["stack"] == "typescript"
    assert "scoped_layers" not in escaped


def test_canonical_symlink_target_cannot_borrow_scopes_across_root(
    tmp_path, fake_openspec
):
    repo = _scoped_repo(tmp_path)
    python = repo / "sdk" / "python"
    python.mkdir(parents=True)
    (python / "zpp.toml").write_text('[tdd]\nstack = "python"\n')
    outside = tmp_path / "outside-link-target"
    (outside / "openspec").mkdir(parents=True)
    (outside / "zpp.toml").write_text('[tdd]\nstack = "typescript"\n')
    link = repo / "linked-outside"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks unavailable: {exc}")

    escaped = governance.resolve_config(link)

    assert escaped["mode"]["root"] == str(outside.resolve())
    assert escaped["effective"]["tdd"]["stack"] == "typescript"
    assert "scoped_layers" not in escaped


def test_profile_is_config_middle_tier(tmp_path, fake_openspec, workspace_file):
    # a self-governed member still gets its workset profile as the middle tier
    worksets.do_import(workspace_file)
    _set_profiles("demo", {"default": {"traits": {"apply": ["ponytail"]}}})
    result = governance.resolve_config(tmp_path / "repo-b")
    assert "ponytail" in result["effective"]["traits"]["apply"]
    assert result["origins"]["traits.apply"].endswith("workset")


def test_profile_extends_one_level(tmp_path, fake_openspec, workspace_file):
    fake_openspec["stores"]["gov"] = str(tmp_path / "gov")
    worksets.do_import(workspace_file)
    side = sidecar.load("demo")
    side["profiles"] = {
        "default": {"traits": {"apply": ["ponytail"]}},
        "store-dev": {"extends": "default", "governance": {"store": "gov"}},
    }
    side["members"]["repo-b"]["profile"] = "store-dev"
    sidecar.save("demo", side)
    result = governance.resolve_config(tmp_path / "repo-b")
    assert "ponytail" in result["effective"]["traits"]["apply"]   # inherited
    assert governance.resolve(tmp_path / "repo-b")["store"] == "gov"  # own


def test_exact_member_path_wins_before_git_alias(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo(repo_a, "https://github.com/example/project.git")
    _init_git_repo(repo_b, "https://github.com/example/project.git")
    workspace.write_text(json.dumps({"folders": [
        {"name": "alpha", "path": "repo-a"},
        {"name": "beta", "path": "repo-b"},
    ]}))
    worksets.do_import(workspace)

    resolved = sidecar.resolve_member(repo_a)

    assert resolved["member"] == "alpha"
    assert resolved["match"] == "path"


def test_independent_clone_aliases_unique_member_by_normalized_remote(
    tmp_path, fake_openspec
):
    workspace = tmp_path / "demo.code-workspace"
    repo_a = tmp_path / "repo-a"
    clone = tmp_path / "project-another-location"
    _init_git_repo(repo_a, "git@github.com:example/project.git")
    _init_git_repo(clone, "https://github.com/example/project")
    workspace.write_text(json.dumps({"folders": [{"name": "alpha", "path": "repo-a"}]}))
    worksets.do_import(workspace)

    resolved = sidecar.resolve_member(clone)

    assert resolved["member"] == "alpha"
    assert resolved["match"] == "git-remote"


def test_linked_worktree_aliases_unique_member_by_common_git_dir(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    repo = tmp_path / "repo-a"
    worktree = tmp_path / "repo-a-feature"
    _init_git_repo(repo)
    _git(repo, "worktree", "add", "-b", "feature-x", str(worktree), "HEAD")
    workspace.write_text(json.dumps({"folders": [{"name": "alpha", "path": "repo-a"}]}))
    worksets.do_import(workspace)

    resolved = sidecar.resolve_member(worktree)

    assert resolved["member"] == "alpha"
    assert resolved["match"] == "git-common-dir"


def test_missing_git_identity_does_not_alias(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    repo = tmp_path / "repo-a"
    alternate = tmp_path / "alternate"
    _init_git_repo(repo)
    alternate.mkdir()
    workspace.write_text(json.dumps({"folders": [{"name": "alpha", "path": "repo-a"}]}))
    worksets.do_import(workspace)

    assert sidecar.resolve_member(alternate) is None


def test_ambiguous_git_remote_alias_fails_closed(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    clone = tmp_path / "project-another-location"
    for repo in (repo_a, repo_b, clone):
        _init_git_repo(repo, "https://github.com/example/project.git")
    workspace.write_text(json.dumps({"folders": [
        {"name": "alpha", "path": "repo-a"},
        {"name": "beta", "path": "repo-b"},
    ]}))
    worksets.do_import(workspace)

    with pytest.raises(sidecar.MemberResolutionError, match="ambiguous"):
        sidecar.resolve_member(clone)


def test_member_override_selects_an_ambiguous_git_alias(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    clone = tmp_path / "project-another-location"
    for repo in (repo_a, repo_b, clone):
        _init_git_repo(repo, "https://github.com/example/project.git")
    workspace.write_text(json.dumps({"folders": [
        {"name": "alpha", "path": "repo-a"},
        {"name": "beta", "path": "repo-b"},
    ]}))
    worksets.do_import(workspace)

    resolved = sidecar.resolve_member(clone, member_override="beta")

    assert resolved["member"] == "beta"
    assert resolved["match"] == "git-remote"


def test_store_backed_feature_checkout_requires_provisioning_read_only(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    project = tmp_path / "project-a"
    store = tmp_path / "governance"
    _init_git_repo(project, "https://github.com/example/project.git")
    _git(project, "checkout", "-b", "feature-x")
    _init_git_repo(store, "https://github.com/example/governance.git")
    (store / ".openspec-store").mkdir()
    (store / ".openspec-store" / "store.yaml").write_text("id: governance\n")
    workspace.write_text(json.dumps({"folders": [
        {"name": "project-a", "path": "project-a"},
        {"name": "governance", "path": "governance"},
    ]}))
    fake_openspec["stores"] = {"governance": str(store)}
    worksets.do_import(workspace)

    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file())
    result = governance.resolve(project)
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file())

    assert "isolation" in result, result
    assert result["isolation"] == {
        "state": "provisioning-required",
        "workset": "demo",
        "member": "project-a",
        "member_match": "path",
        "project_branch": "feature-x",
        "governance_branch": "project-a/feature-x",
        "store": "governance",
        "base_root": str(store.resolve()),
        "effective_root": str((tmp_path / "zpp-home" / "worksets" / "demo" / "governance-worktrees" / "project-a" / "feature-x").resolve()),
        "remediation": f"zpp workset open demo --project {project.resolve()}",
    }
    assert before == after


def test_provision_creates_then_reuses_isolated_governance_worktree(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    project = tmp_path / "project-a"
    store = tmp_path / "governance"
    _init_git_repo(project)
    _git(project, "checkout", "-b", "feature-x")
    _init_git_repo(store)
    (store / ".openspec-store").mkdir()
    (store / ".openspec-store" / "store.yaml").write_text("id: governance\n")
    workspace.write_text(json.dumps({"folders": [
        {"name": "project-a", "path": "project-a"},
        {"name": "governance", "path": "governance"},
    ]}))
    worksets.do_import(workspace)

    created = isolation.provision("demo", project, base_override="HEAD")
    reused = isolation.provision("demo", project, base_override="HEAD")

    assert created["governance_branch"] == "project-a/feature-x"
    assert created["reused"] is False
    assert Path(created["effective_root"]).is_dir()
    assert reused["effective_root"] == created["effective_root"]
    assert reused["reused"] is True


def test_resolve_config_reads_the_provisioned_effective_store_root(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    project = tmp_path / "project-a"
    store = tmp_path / "governance"
    _init_git_repo(project)
    _git(project, "checkout", "-b", "feature-x")
    _init_git_repo(store)
    (store / ".openspec-store").mkdir()
    (store / ".openspec-store" / "store.yaml").write_text("id: governance\n")
    (store / "zpp.toml").write_text('[profiles.default.agent]\nmode = "isolated"\n')
    _git(store, "add", ".openspec-store/store.yaml", "zpp.toml")
    _git(store, "commit", "-m", "publish defaults")
    workspace.write_text(json.dumps({"folders": [
        {"name": "project-a", "path": "project-a"},
        {"name": "governance", "path": "governance"},
    ]}))
    fake_openspec["stores"] = {"governance": str(store)}
    worksets.do_import(workspace)

    isolation.provision("demo", project, base_override="HEAD")
    resolved = governance.resolve_config(project)

    assert resolved["mode"]["isolation"]["state"] == "ready"
    assert resolved["effective"]["agent"]["mode"] == "isolated"


def test_default_store_base_comes_from_origin_head(tmp_path):
    remote = tmp_path / "remote.git"
    store = tmp_path / "store"
    _git(tmp_path, "init", "--bare", str(remote))
    _init_git_repo(store)
    _git(store, "branch", "-M", "main")
    _git(store, "remote", "add", "origin", str(remote))
    _git(store, "push", "-u", "origin", "main")
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(store, "remote", "set-head", "origin", "-a")

    assert governance.adapter.git_default_branch(store) == "main"
    assert governance.adapter.git_default_ref(store) == "origin/main"


def test_missing_base_preflight_leaves_no_governance_worktree_parent(
    tmp_path, fake_openspec
):
    workspace = tmp_path / "demo.code-workspace"
    project = tmp_path / "project-a"
    store = tmp_path / "governance"
    _init_git_repo(project)
    _init_git_repo(store)
    (store / ".openspec-store").mkdir()
    (store / ".openspec-store" / "store.yaml").write_text("id: governance\n")
    workspace.write_text(json.dumps({"folders": [
        {"name": "project-a", "path": "project-a"},
        {"name": "governance", "path": "governance"},
    ]}))
    worksets.do_import(workspace)

    with pytest.raises(isolation.IsolationError, match="base ref"):
        isolation.provision("demo", project, base_override="does-not-exist")

    generated = tmp_path / "zpp-home" / "worksets" / "demo" / "governance-worktrees"
    assert not generated.exists()


def test_session_cleanup_removes_generated_view_and_worktree_only(
    tmp_path, fake_openspec
):
    workspace = tmp_path / "demo.code-workspace"
    project = tmp_path / "project-a"
    store = tmp_path / "governance"
    _init_git_repo(project)
    _init_git_repo(store)
    (store / ".openspec-store").mkdir()
    (store / ".openspec-store" / "store.yaml").write_text("id: governance\n")
    workspace.write_text(json.dumps({"folders": [
        {"name": "project-a", "path": "project-a"},
        {"name": "governance", "path": "governance"},
    ]}))
    original_workspace = workspace.read_bytes()
    worksets.do_import(workspace)

    opened = isolation.open_session(project, base_override="HEAD")
    cleaned = isolation.cleanup_session(opened["session_view"])
    repeated = isolation.cleanup_session(opened["session_view"])

    assert cleaned["removed"] is True
    assert repeated["removed"] is False
    assert not Path(opened["effective_root"]).exists()
    assert opened["session_view"] not in fake_openspec["worksets"]
    assert workspace.read_bytes() == original_workspace


def test_status_and_doctor_report_interrupted_session_view(tmp_path, fake_openspec):
    workspace = tmp_path / "demo.code-workspace"
    project = tmp_path / "project-a"
    store = tmp_path / "governance"
    _init_git_repo(project)
    _init_git_repo(store)
    (store / ".openspec-store").mkdir()
    (store / ".openspec-store" / "store.yaml").write_text("id: governance\n")
    workspace.write_text(json.dumps({"folders": [
        {"name": "project-a", "path": "project-a"},
        {"name": "governance", "path": "governance"},
    ]}))
    worksets.do_import(workspace)
    opened = isolation.open_session(project, base_override="HEAD")

    status = worksets.status("demo")
    del fake_openspec["worksets"][opened["session_view"]]
    findings = worksets.doctor()

    assert status["sessions"][0]["state"] == "ready"
    assert any(
        opened["session_view"] in finding["problem"]
        and "interrupted" in finding["problem"]
        for finding in findings
    )


def test_legacy_multi_store_resolution_has_structured_invalid_workset_shape(
    tmp_path, fake_openspec
):
    project = tmp_path / "project"
    project.mkdir()
    stores = []
    for name in ("governance-a", "governance-b"):
        root = tmp_path / name
        (root / ".openspec-store").mkdir(parents=True)
        (root / ".openspec-store" / "store.yaml").write_text(f"id: {name}\n")
        stores.append({"name": name, "path": str(root)})
    workspace = tmp_path / "legacy.code-workspace"
    workspace.write_text("{}")
    sidecar.save(
        "legacy",
        sidecar.new(
            workspace,
            [{"name": "project", "path": str(project)}, *stores],
        ),
    )

    result = governance.resolve(project)

    assert result["isolation"] == {
        "state": "invalid-workset",
        "reason": "multiple-dedicated-stores",
        "workset": "legacy",
        "stores": ["governance-a", "governance-b"],
        "remediation": "keep one .openspec-store member or split the workset",
    }
