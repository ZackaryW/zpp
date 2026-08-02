---
name: use-rg
description: Prefer ripgrep for repository text and file discovery
order: 300
config:
  useThis: true
skill_lookup: []
---
Use `rg` for recursive text search and `rg --files` for file discovery. Narrow
patterns and paths before broad scans, and fall back only when ripgrep cannot
perform the required lookup.
