# Split Overlap Check

Check whether exact text values appear in both JSONL data splits. The tool reports line numbers only; it never prints input values, paths, or field names.

## Install and run

Python 3.10 or newer is required. Runtime dependencies are Python's standard library only.

```console
python -m pip install .
split-overlap-check left.jsonl right.jsonl --field text
```

For development, install the test extra and run `python -m pytest`.

Each nonblank line must be a UTF-8 JSON object whose selected top-level field is a string. Empty files are valid. Duplicate JSON keys, nonstandard constants, malformed records, blank lines, and unreadable inputs are invalid. On invalid input or command misuse, the command prints only `{"status":"invalid_input"}` to stdout and exits 2. A clear comparison exits 0; overlap exits 1.

Successful output contains `status` (`clear` or `overlap`) and `matches`. Every match group gives sorted, one-based `left_lines` and `right_lines`; groups follow the first occurrence order in the left input. Equality is exact Unicode string equality: there is no trimming, normalization, or fuzzy matching.

## Limits

Both complete files are read and validated before any result is emitted. Memory use grows with the inputs and their distinct values. The tool checks exact text overlap only; it does not assess semantic similarity, split quality, or guarantee leakage-free evaluation. It does not generate splits or support nested field paths. Use synthetic or appropriately approved data when demonstrating the tool.

## Example

```console
split-overlap-check examples/left.jsonl examples/right.jsonl --field text
```
