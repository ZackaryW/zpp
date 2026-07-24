"""OpenSpec-valid Pathverse date-addressed change ids."""

import re


VALID = re.compile(r"^c\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*$")
NUMERIC = re.compile(r"^(\d{6})-([a-z0-9]+(?:-[a-z0-9]+)*)$")


class ChangeIdError(ValueError):
    pass


def validate(value: str) -> str:
    if VALID.fullmatch(value):
        return value
    numeric = NUMERIC.fullmatch(value)
    if numeric:
        normalized = f"c{value}"
        raise ChangeIdError(
            f"change ids must begin with a letter for OpenSpec; use '{normalized}'"
        )
    raise ChangeIdError(
        "change id must match cYYMMDD-<descriptive-name> using lowercase words"
    )
