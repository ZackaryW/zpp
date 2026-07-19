# Tasks: bootstrap-drop-saucepan

## 1. Fail-first coverage

- [x] 1.1 pytest: failing tests — bootstrap with saucepan absent + release
      unreachable neither fetches nor emits a manual step; doctor exits 0
      with all core tools present and saucepan absent (row shows
      absent-optional).
- [x] 1.2 behave: failing scenario in the doctor feature — bootstrap ignores
      the optional tool; doctor stays green without it.

## 2. Implement

- [x] 2.1 Mark saucepan `optional` in the toolchain table; bootstrap skips
      optional rows; doctor keeps the row but excludes optional absences
      from the exit-1 predicate.
- [x] 2.2 Full suite green; existing managed-mode scenarios untouched.

## 3. Close

- [x] 3.1 README doctor/bootstrap paragraph: saucepan is optional, fetched on
      first `zpp trait fetch`.
- [x] 3.2 `openspec validate --specs` passes; commit per zmem grammar.
