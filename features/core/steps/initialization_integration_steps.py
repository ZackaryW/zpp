from behave import given, then, when

from features.support import initialization_integration_support as integration


given("Pi, Codex, and Claude Code have no global ZPP workflow integration")(
    integration.no_global_integrations
)
given("the existing default profile has distinguishable user-authored content")(
    integration.distinct_authored_default
)
given("Pi has a complete compatible global ZPP workflow integration surrounded by unmanaged content")(
    integration.compatible_pi_surrounded
)
given("Pi's complete global integration is recorded")(integration.record_pi_complete)
given("Codex has compatible generated global OpenSpec skills but no ZPP workflow bundle or native hooks")(
    integration.partial_codex_openspec_only
)
given("Codex's generated OpenSpec skills and repository-local projections are recorded")(
    integration.record_codex_openspec_and_local
)
given("Pi has an intact outdated managed global ZPP workflow bundle")(
    integration.outdated_pi_integration
)
given("Pi's OpenSpec projection records a different version from the detected OpenSpec version")(
    integration.assert_pi_openspec_is_outdated
)
given("unrelated Pi content is recorded")(integration.record_unrelated_pi)
given("every other Claude Code global integration destination is recorded")(
    integration.record_all_claude_destinations
)
given("Pi has no global ZPP workflow integration")(
    integration.pi_has_no_global_integration
)
given("Codex has an unmanaged conflict at a required global OpenSpec skill destination")(
    integration.codex_openspec_conflict
)
given("every selected agent global integration destination is recorded")(
    integration.record_selected_destinations
)

when("the user runs zpp init with agent Codex")(integration.run_init_codex)
when("the user runs zpp init with agent Pi")(integration.run_init_pi)

then("no workflow or OpenSpec skill projection exists")(
    integration.no_skill_projection_exists
)
then("no workflow or OpenSpec skill projection is created or changed")(
    integration.no_selected_surface_changed
)
then("Pi has the complete current global ZPP workflow integration")(
    integration.assert_pi_complete
)
then("Codex has the complete current global ZPP workflow integration")(
    integration.assert_codex_complete
)
then("Claude Code has the complete current global ZPP workflow integration")(
    integration.assert_claude_complete
)
then("Codex has the complete current global ZPP workflow integration under its native locations")(
    integration.assert_codex_complete_native_roots
)
then("every generated OpenSpec projection records the detected version")(
    integration.assert_generated_versions
)
then("OpenSpec generation uses an isolated temporary project that is removed")(
    integration.assert_generation_boundary
)
then("neither agent receives a ZPP instruction paragraph")(
    integration.assert_no_instruction_paragraphs
)
then("Claude Code receives no ZPP instruction paragraph")(
    integration.assert_claude_no_instruction_paragraph
)
then("Pi's complete global integration is byte-for-byte unchanged")(
    integration.assert_pi_complete_unchanged
)
then("the existing default profile is byte-for-byte unchanged")(
    integration.assert_default_unchanged
)
then("Codex's generated OpenSpec skills are byte-for-byte unchanged")(
    integration.assert_codex_openspec_unchanged
)
then("Codex's repository-local projections are byte-for-byte unchanged")(
    integration.assert_codex_local_unchanged
)
then("Pi records the newly detected OpenSpec version")(
    integration.assert_pi_new_openspec_version
)
then("unrelated Pi content is byte-for-byte unchanged")(
    integration.assert_unrelated_pi_unchanged
)
then("every Claude Code global integration destination is byte-for-byte unchanged")(
    integration.assert_all_claude_destinations_unchanged
)
then("every selected agent global integration destination is byte-for-byte unchanged")(
    integration.assert_selected_destinations_unchanged
)
then("init help describes missing-state bootstrap and complete global setup for selected agents")(
    integration.assert_init_help
)
