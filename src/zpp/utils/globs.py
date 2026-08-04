from __future__ import annotations

import re
from functools import lru_cache


def glob_full_match(path: str, pattern: str) -> bool:
    """Return whether ``path`` matches ``pattern`` using anchored glob semantics.

    This mirrors :meth:`pathlib.PurePosixPath.full_match` (added in Python 3.13):
    the pattern is matched against the whole path, ``**`` matches any number of
    path segments (including zero), and ``*``, ``?`` and ``[...]`` match within a
    single segment only.
    """
    return _compiled_pattern(pattern).match(path) is not None


@lru_cache(maxsize=None)
def _compiled_pattern(pattern: str) -> re.Pattern[str]:
    segments = pattern.split("/")
    parts: list[str] = []
    for index, segment in enumerate(segments):
        last = index == len(segments) - 1
        if segment == "**":
            # ``**`` matches zero or more segments. When not the final segment it
            # optionally consumes the following separator so it can match nothing.
            parts.append(".*" if last else "(?:.*/)?")
        else:
            parts.append(_translate_segment(segment))
            if not last:
                parts.append("/")
    return re.compile("".join(parts) + r"\Z")


def _translate_segment(segment: str) -> str:
    result: list[str] = []
    index = 0
    length = len(segment)
    while index < length:
        char = segment[index]
        if char == "*":
            result.append("[^/]*")
            index += 1
        elif char == "?":
            result.append("[^/]")
            index += 1
        elif char == "[":
            end = index + 1
            if end < length and segment[end] in "!]":
                end += 1
            while end < length and segment[end] != "]":
                end += 1
            if end >= length:
                result.append(re.escape("["))
                index += 1
            else:
                body = segment[index + 1 : end].replace("\\", "\\\\")
                if body.startswith("!"):
                    body = "^" + body[1:]
                result.append("[" + body + "]")
                index = end + 1
        else:
            result.append(re.escape(char))
            index += 1
    return "".join(result)
