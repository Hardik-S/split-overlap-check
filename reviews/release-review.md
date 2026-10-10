# Independent frozen-contract review

**Result:** PASS for the implementation and verification reviewed below. No material contract gap found in PR #2.

**Release gate:** The repository is public and the launch note is present, but `v0.1.0` is not yet tagged and no GitHub release is listed. The public tagged release gate is therefore still pending; this review did not create a tag or release.

**Reviewed revision:** `2fd90b43b75a12a1acf38b98ce5906099719ac59` (`Avoid shell-dependent quoting in installed CI probe`), on `feat/split-overlap-v0.1.0`.

## Contract review

Compared `CONTRACT.md` with `src/split_overlap_check/core.py`, `src/split_overlap_check/cli.py`, the README, launch note, tests, and CI workflow. The implementation validates both files fully before producing output; decodes strict UTF-8; accepts LF, CRLF, and CR record boundaries; rejects blank/malformed records, duplicate keys, nonstandard constants, missing or non-string top-level fields, and unreadable paths; groups exact strings by sorted one-based line numbers in first-left-line order; and emits no source values or exception details. Empty files and one-sided repetitions behave as specified. CLI misuse emits the value-free JSON error with exit 2 and empty stderr; `--help` remains standard.

The workflow installs the package and test extra, runs pytest, and invokes the installed command. Its matrix covers Ubuntu and Windows with Python 3.10 and 3.13. The latest PR checks reported pass for all eight matrix jobs (two runs) and GitGuardian.

## Verification evidence

Fresh environment used Python 3.13.1 on Windows, created outside the checkout:

```powershell
$reviewEnv = Join-Path $env:TEMP 'split-overlap-review-20261010'
py -3.13 -m venv $reviewEnv
& (Join-Path $reviewEnv 'Scripts\python.exe') -m pip install '.[test]'
& (Join-Path $reviewEnv 'Scripts\python.exe') -m pytest -q
```

Result: package built and installed successfully; **20 passed**.

Installed console-entry-point probes used `Scripts\split-overlap-check.exe` with temporary synthetic files:

| Probe | Result |
| --- | --- |
| Repeated exact overlap, CRLF input, and group ordering | Exit 1; `{"status":"overlap","matches":[{"left_lines":[1,3],"right_lines":[2,3]},{"left_lines":[2],"right_lines":[1]}]}`; empty stderr |
| Clear comparison | Exit 0; `{"status":"clear","matches":[]}`; empty stderr |
| Valid matching prefix followed by malformed suffix containing sentinel strings | Exit 2; exactly `{"status":"invalid_input"}`; empty stderr; no sentinel/path echoed |
| Duplicate JSON key, `NaN`, blank line, and missing input file | Each exit 2; exactly `{"status":"invalid_input"}`; empty stderr |
| Unicode strings differing only by composed/decomposed accent | Exit 1; two separate exact-match groups, confirming no normalization |
| No-argument misuse | Exit 2; exactly `{"status":"invalid_input"}`; empty stderr |
| `--help` | Exit 0; standard usage text; empty stderr |

Unit tests additionally cover invalid UTF-8, invalid JSON suffixes, nested-key handling, empty files, CR/LF/CRLF, and Unicode separator characters.

CI was inspected with:

```powershell
$env:GH_CONFIG_DIR='C:\Users\hshre\OneDrive\Documents\42 - Agents\Codex\MeaningfulGitContributionGardener\.ghcfg'
gh pr checks 2 --repo Hardik-S/split-overlap-check
```

All reported CI matrix checks passed at review time.

## Limits and remaining gate

This was a bounded contract and acceptance review, not a performance, memory-pressure, packaging-across-all-supported-Python-versions, or semantic-leakage audit. The project documents the intended exact-match and memory limitations. No code repairs, merge, tag, or release were performed. `v0.1.0` tag lookup returned HTTP 404 and the release list was empty at review time, so publishing that release remains a separate required gate.
