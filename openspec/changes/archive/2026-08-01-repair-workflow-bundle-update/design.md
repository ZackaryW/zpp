## Context

See `proposal.md` for motivation and `specs/workflow-skill-distribution/spec.md` for the behavioral contract. Manifest decoding currently embeds the current eight-skill inventory, and projection inspection also reads the current inventory rather than the inventory owned by the selected manifest. As a result, adding a skill makes an intact earlier projection impossible to inspect as outdated.

## Goals / Non-Goals

**Goals:**

- Separate historical ownership validation from current-bundle compatibility.
- Replace only paths proved to be owned by the selected historical manifest.
- Keep multi-destination preflight and rollback behavior unchanged.
- Give absent, malformed/conflicting, and outdated states distinct outcomes.

**Non-Goals:**

- Automatic scope selection or fallback from local to global.
- Repairing a manifest whose declared files no longer match disk.
- Letting `--force` overwrite conflicts or user-owned content.
- Changing the manifest schema version or introducing a dependency.

## Decisions

### Validate manifest structure independently of the current inventory

Keep schema version 1, normalized relative-path and digest validation, and the requirement that every manifest-owned skill directory contains its own `SKILL.md`. Permit a historical manifest to own a safe subset of permanent `zpp-*` skill directories instead of requiring every current skill name.

Treating the current inventory as schema validity was rejected because inventory growth is a compatibility difference, not ownership corruption.

### Inspect exactly the manifest-owned projection

Derive the historical top-level skill directories from the manifest. Read every file under those directories, reject symlinks and unexpected or missing files, and compare exact bytes and the recorded fingerprint. Only after ownership integrity passes, compare bundle version and fingerprint with the packaged bundle to classify the projection as compatible or outdated.

Reading the current packaged inventory first was rejected because a newly added skill is expected to be absent from an older projection.

### Retain manifest-bounded replacement

For an outdated projection, stage removal of only the top-level directories represented by the historical manifest plus its manifest file, then create the complete current projection through the existing atomic lifecycle plan. Unrelated sibling skills remain outside both removal and creation plans.

### Report absence before unmanaged state

Update and removal planning SHALL identify an `absent` inspection separately. Conflict states continue to use managed-state rejection because they contain files or metadata that cannot be safely proven as the selected ZPP projection.

## Risks / Trade-offs

- **[A forged manifest claims user content]** → Continue requiring a regular manifest, safe `zpp-*` paths, complete per-skill documents, exact file sets, exact digests, and fingerprint agreement before treating it as managed.
- **[Historical directory contains later user edits]** → Classify it as conflict and perform no replacement.
- **[A future skill is renamed or removed]** → Keep structural ownership decoding independent of the current inventory so its manifest-owned directory can still be removed safely during update.
- **[Global and local versions differ]** → Preserve explicit scope and existing coexistence reporting; never choose a scope implicitly.

## Migration Plan

1. Ship the tolerant historical-manifest reader and manifest-driven projection inspection.
2. Run `zpp workflow update --global --agent codex` against the existing seven-skill manifest.
3. Verify the new eight-skill manifest and exact installed content while preserving unrelated global skills.
4. If replacement fails, rely on the existing staged-removal rollback to restore the historical projection.
