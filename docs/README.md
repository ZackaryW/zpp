# ZPP documentation

The root [README](../README.md) is the product landing page. These pages own the
detailed documentation for each part of ZPP so command reference, trait semantics,
workflow policy, and coordination mechanics do not compete in one monolithic file.

## Start here

- The root [Getting started](../README.md#getting-started) section covers installation,
  initialization, and the first resolution.
- [Traits and resolution](traits.md) explains repository context, trait families,
  selection, activation, evidence, and provenance.
- [Agent workflows](workflows.md) describes the packaged workflow family, companion
  skills, native hooks, and reminder runs.
- [Repository verification](verification.md) explains optional affected verification
  through `zpp.behave.yaml` and direct native BDD execution.
- [OpenSpec and Bundler coordination](coordination.md) covers stores, atomic leases,
  audits, archives, and exceptional bypass.
- [CLI reference](cli.md) lists the current public command shapes and points to the
  topic that owns each command's semantics.

## Mental model

ZPP has four cooperating surfaces:

1. Traits contribute small repository-selected instruction bodies.
2. Agent Router projects the workflow family, companion skills, and native context
   hooks into supported coding agents.
3. OpenSpec Bundler supplies repository/store topology and atomic mutation leases.
4. `zpp behave` optionally coordinates repository-owned verification targets.

The surfaces are deliberately separate. Traits do not control workflow authority,
workflow reminders do not grant mutation authority, and the presence of a behavior
mapping does not execute tests.
