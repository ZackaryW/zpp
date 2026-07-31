from __future__ import annotations

import sys
from enum import Enum
from typing import Callable, TypeVar

import typer

from zpp.core.errors import ZppDomainError, validation_diagnostic
from zpp.utils.models import ManagedStateError, ZppValidationError


class AgentOption(str, Enum):
    pi = "pi"
    codex = "codex"
    claude = "claude"


Result = TypeVar("Result")


def interactive_terminal_available() -> bool:
    return sys.stdin.isatty()


def run_domain(action: Callable[[], Result]) -> Result | None:
    try:
        return action()
    except typer.Exit:
        raise
    except ZppValidationError as error:
        typer.echo(validation_diagnostic(error), err=True)
    except (ZppDomainError, ManagedStateError, OSError, UnicodeError, ValueError) as error:
        typer.echo(str(error), err=True)
    raise typer.Exit(1)
