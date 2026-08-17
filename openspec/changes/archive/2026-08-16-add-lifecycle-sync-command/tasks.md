## 1. Shared lifecycle projection inventory

- [x] 1.1 Prove fail-first that one inventory yields inspect, project, and remove for every per-agent entry in deterministic order
- [x] 1.2 Generalize the inventory currently private to `reset_projections` to carry a projection callable
- [x] 1.3 Prove fail-first that the inventory reflects the discovered companion skill set without a maintained name list

## 2. Drift selection

- [x] 2.1 Prove fail-first that drift selection reprojects only entries whose observed state is not current
- [x] 2.2 Prove fail-first that forced selection returns every owned entry while still excluding unmanaged and mismatched entries
- [x] 2.3 Implement the selection seam over the shared inventory

## 3. Synchronization command

- [x] 3.1 Shape the observable synchronization behavior as scenarios bound to the public CLI
- [x] 3.2 Wire `zpp sync` through the shared inventory and selection seam
- [x] 3.3 Bind interactive agent selection and the concise summary, keeping JSON behind `--json`
- [x] 3.4 Register the command in the public application

## 4. Initialization boundary

- [x] 4.1 Shape the observable initialization rejection behavior as scenarios bound to the public CLI
- [x] 4.2 Reject a selected agent carrying any ZPP projection and direct it to `zpp sync`
- [x] 4.3 Initialize selected agents carrying no projection in the same invocation
- [x] 4.4 Remove the `--force` option and reject it as unsupported

## 5. Specification reconciliation

- [x] 5.1 Reconcile the four requirements into `product-home-lifecycle`
- [x] 5.2 Broaden the `product-home-lifecycle` Purpose to the complete integration lifecycle by editing the canonical spec directly

## 6. Finalization

- [x] 6.1 Run strict OpenSpec validation and the complete established verification set
- [ ] 6.2 Archive the change and commit the logical update
