# Tasks: config-empty-hint

## 1. Fail-first coverage

- [x] 1.1 pytest: failing tests — empty resolve human output contains the
      hint; `--json` output is the bare empty result; a non-empty resolve
      shows no hint.

## 2. Implement

- [x] 2.1 Append the hint in `zpp/cli/config.py` when the effective config is
      empty (human path only); full suite green.

## 3. Close

- [x] 3.1 README: commented `zpp.toml` template section ([governance],
      [tdd]/[bdd], [traits] apply, [doctor]).
- [x] 3.2 `openspec validate --specs` passes; commit per zmem grammar.
