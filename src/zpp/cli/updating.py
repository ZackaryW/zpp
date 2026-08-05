from __future__ import annotations

from pathlib import Path

from zpp.cli.shared import run_domain
from zpp.core.updating import update_global_state


def update_command() -> None:
    """Refresh initialized global ZPP state and installed integrations.

    This command does not upgrade the running ZPP executable.
    """
    run_domain(lambda: update_global_state(Path.home()))
