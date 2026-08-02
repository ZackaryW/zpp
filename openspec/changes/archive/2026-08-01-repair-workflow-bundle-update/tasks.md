## 1. Historical manifest compatibility

- [x] 1.1 Verify structurally valid historical manifests and manifest-owned projection contents independently of the current bundle inventory.
- [x] 1.2 Classify intact historical projections as outdated while preserving conflict rejection for unsafe, malformed, missing, or changed ownership evidence.

## 2. Lifecycle behavior

- [x] 2.1 Replace historical manifest-owned paths atomically with the current complete bundle while preserving unrelated skills and scopes.
- [x] 2.2 Report an absent selected projection distinctly from unmanaged or conflicting content.

## 3. End-to-end update

- [x] 3.1 Verify utility behavior through TDD and workflow lifecycle behavior through Behave.
- [x] 3.2 Update the user-global Codex projection through `zpp workflow update --global --agent codex` and verify the current manifest and eight-skill bundle.
