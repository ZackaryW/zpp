---
name: codespace-claim-guard
description: Verify one machine-local codespace claim before mutation
order: 110
config:
  useThis: true
---
Before mutating a ZPP-managed checkout, obtain or verify the active codespace
claim for the complete writable target set. Treat OpenSpec worksets only as
optional opening projections. Supported agent hooks reject explicit direct
writes into another active claim; shell association is cooperative and does not
promise universal filesystem isolation.
