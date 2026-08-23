## REMOVED Requirements

### Requirement: Declared affected claim before worktree modification
**Reason**: Bundler store/change members are supplied directly at automatic workflow acquisition, so a separate OpenLease claim is obsolete.
**Migration**: None. The workflow acquires its exact members before mutation.

### Requirement: Closure resolution and lockability evaluation
**Reason**: Bundler expands parent descendants and evaluates conflicts atomically during acquisition; ZPP retains no dependency closure or preview phase.
**Migration**: Declare independent participants as explicit multi-root members.

### Requirement: Explicit go-ahead before permit acquisition
**Reason**: The owner selected automatic workflow acquisition rather than the former claim/preview/go-ahead sequence.
**Migration**: None. A Bundler conflict blocks mutation directly.

### Requirement: Explicit unlock as guarantee check
**Reason**: Bundler retains a complete bundle until all members archive and the workflow explicitly completes it.
**Migration**: Use archive recording and bundle completion; use owner-authorized bundle abandonment only for recovery.
