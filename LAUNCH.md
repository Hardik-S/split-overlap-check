# v0.1.0 launch note

Split Overlap Check is a small offline Python CLI for detecting exact text overlap between two JSONL splits. Install with `python -m pip install .`, then run `split-overlap-check LEFT.jsonl RIGHT.jsonl --field text`.

The command validates both complete inputs before reporting one-based line groups. It exits 0 for clear, 1 for overlap, and 2 for invalid input or command misuse. Errors contain no input data. Runtime behavior uses only the Python standard library.

This release is an exact-match aid, not a semantic or data-quality audit. It does not normalize text, produce splits, or establish that an evaluation dataset is leakage-free. Memory use is proportional to the input data and groups.
