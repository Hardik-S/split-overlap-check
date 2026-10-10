import json
import os
import subprocess
import sys


def run(*args):
    return subprocess.run([sys.executable, "-m", "split_overlap_check.cli", *map(str, args)], capture_output=True, text=True)


def test_overlap_and_clear_output_do_not_echo_data(tmp_path):
    left, right = tmp_path / "left", tmp_path / "right"
    left.write_text('{"text":"SECRET VALUE"}\n', encoding="utf-8")
    right.write_text('{"text":"SECRET VALUE"}\n', encoding="utf-8")
    overlap = run(left, right, "--field", "text")
    assert overlap.returncode == 1 and overlap.stderr == ""
    assert json.loads(overlap.stdout) == {"status": "overlap", "matches": [{"left_lines": [1], "right_lines": [1]}]}
    assert "SECRET" not in overlap.stdout and str(left) not in overlap.stdout
    right.write_text('{"text":"different"}\n', encoding="utf-8")
    clear = run(left, right, "--field", "text")
    assert clear.returncode == 0 and json.loads(clear.stdout) == {"status": "clear", "matches": []}


def test_invalid_suffix_has_no_partial_output_and_no_echo(tmp_path):
    left, right = tmp_path / "left", tmp_path / "right"
    left.write_text('{"secret_field":"sensitive value"}\ninvalid secret payload\n', encoding="utf-8")
    right.write_text('{"secret_field":"sensitive value"}\n', encoding="utf-8")
    result = run(left, right, "--field", "secret_field")
    assert result.returncode == 2
    assert result.stdout == '{"status":"invalid_input"}\n' and result.stderr == ""
    assert "sensitive" not in result.stdout and str(left) not in result.stdout and "secret_field" not in result.stdout


def test_misuse_is_value_free_json_and_help_is_standard():
    invalid = run()
    assert invalid.returncode == 2 and invalid.stdout == '{"status":"invalid_input"}\n' and invalid.stderr == ""
    help_result = run("--help")
    assert help_result.returncode == 0 and "usage:" in help_result.stdout and help_result.stderr == ""
