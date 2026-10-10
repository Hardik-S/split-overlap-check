"""Core validation and exact-text grouping logic."""

import json
import re
from pathlib import Path
from typing import Any


class InvalidInput(Exception):
    """An input file cannot be used under the CLI contract."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key")
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise ValueError("nonstandard JSON constant")


def read_split(path: str | Path, field: str) -> list[tuple[str, int]]:
    """Read and validate one UTF-8 JSONL split, retaining exact values and line numbers."""
    try:
        text = Path(path).read_bytes().decode("utf-8")
    except (OSError, UnicodeError):
        raise InvalidInput from None

    if text == "":
        return []
    # JSONL permits the common newline encodings; do not split on Unicode separators
    # that may occur as valid characters inside a JSON string.
    lines = re.split(r"\r\n|\r|\n", text)
    if lines[-1] == "":
        lines.pop()
    records: list[tuple[str, int]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise InvalidInput
        try:
            obj = json.loads(
                line, object_pairs_hook=_unique_object, parse_constant=_reject_constant
            )
        except (json.JSONDecodeError, ValueError, RecursionError):
            raise InvalidInput from None
        if not isinstance(obj, dict) or not isinstance(obj.get(field), str):
            raise InvalidInput
        records.append((obj[field], line_number))
    return records


def find_matches(left: list[tuple[str, int]], right: list[tuple[str, int]]) -> list[dict[str, list[int]]]:
    """Return grouped cross-split exact string matches in first-left-line order."""
    left_groups: dict[str, list[int]] = {}
    right_groups: dict[str, list[int]] = {}
    for value, line in left:
        left_groups.setdefault(value, []).append(line)
    for value, line in right:
        right_groups.setdefault(value, []).append(line)
    return [
        {"left_lines": left_groups[value], "right_lines": right_groups[value]}
        for value in left_groups
        if value in right_groups
    ]
