"""Command-line interface."""

import argparse
import json
import sys

from .core import InvalidInput, find_matches, read_split


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # noqa: ARG002
        raise InvalidInput


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="split-overlap-check", description="Check exact text overlap between two JSONL splits.")
    parser.add_argument("left", help="left JSONL split")
    parser.add_argument("right", help="right JSONL split")
    parser.add_argument("--field", required=True, help="top-level field containing text")
    try:
        args = parser.parse_args(argv)
        left = read_split(args.left, args.field)
        right = read_split(args.right, args.field)
        matches = find_matches(left, right)
    except InvalidInput:
        print('{"status":"invalid_input"}')
        return 2
    status = "overlap" if matches else "clear"
    print(json.dumps({"status": status, "matches": matches}, separators=(",", ":")))
    return 1 if matches else 0


if __name__ == "__main__":
    sys.exit(main())
