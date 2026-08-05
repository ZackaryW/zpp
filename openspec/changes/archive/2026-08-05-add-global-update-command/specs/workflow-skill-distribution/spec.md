## ADDED Requirements

### Requirement: Automatic maintenance of installed global workflows
Top-level `zpp update` SHALL inspect the supported Pi, Codex, and Claude Code global workflow locations without requiring agent selection. Every compatible or outdated managed ZPP workflow bundle it discovers SHALL be maintained as one complete integration with the current packaged ZPP bundle, current native lifecycle hooks, and OpenSpec core operation skills generated for that agent by the installed OpenSpec version. An absent ZPP workflow bundle SHALL remain absent and SHALL NOT cause its agent's OpenSpec skill projection to be installed merely because another owned surface is present.

For a discovered managed workflow bundle, global update SHALL repair an absent managed OpenSpec projection, preserve a verified projection when its recorded OpenSpec version matches the detected value, and regenerate it only when the detected value differs, including `null` comparison. It SHALL obtain OpenSpec-owned content through isolated platform-neutral OpenSpec generation and SHALL preserve unrelated agent content.

Global update SHALL preflight every discovered workflow, generated OpenSpec skill set, destination, hook, and persistent-default mutation before changing any included surface. A malformed ownership manifest, modified managed content, unsafe path, unmanaged collision, generation failure, or profile conflict SHALL reject the complete update without partial changes. Repository-local projections SHALL remain untouched.

#### Scenario: Refresh all installed managed global workflows
- **WHEN** global update discovers managed global workflow bundles for any combination of supported agents
- **THEN** it updates every discovered bundle and its complete hook and OpenSpec integration while leaving agents without a bundle uninstalled

#### Scenario: Preserve matching OpenSpec projections
- **WHEN** a discovered workflow's verified OpenSpec projection records the currently detected version value
- **THEN** global update preserves that projection byte-for-byte

#### Scenario: Regenerate changed OpenSpec projections
- **WHEN** a discovered workflow's OpenSpec projection is absent or records a different version value
- **THEN** global update installs or regenerates only that managed generated projection from the current isolated OpenSpec output

#### Scenario: Reject a discovered workflow conflict atomically
- **WHEN** any discovered workflow integration or the persistent default cannot be safely preflighted
- **THEN** global update identifies the conflict and changes none of the discovered global or local surfaces

#### Scenario: Keep local workflow state isolated
- **WHEN** compatible or conflicting repository-local workflow projections exist during global update
- **THEN** global update does not inspect them as update targets and leaves them unchanged

#### Scenario: Repeat global update idempotently
- **WHEN** every discovered global surface and the persistent default already match the current compatible state
- **THEN** global update succeeds without rewriting managed, authored, generated, or unrelated content
