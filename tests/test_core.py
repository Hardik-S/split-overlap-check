import json

import pytest

from split_overlap_check.core import InvalidInput, find_matches, read_split


def write(tmp_path, name, data):
    path = tmp_path / name
    path.write_bytes(data)
    return path


@pytest.mark.parametrize("newline", [b"\n", b"\r\n", b"\r"])
def test_newlines_and_sorted_line_numbers(tmp_path, newline):
    left = write(tmp_path, "l", newline.join([b'{"text":"b"}', b'{"text":"a"}', b'{"text":"b"}']) + newline)
    right = write(tmp_path, "r", newline.join([b'{"text":"a"}', b'{"text":"b"}', b'{"text":"b"}']))
    result = find_matches(read_split(left, "text"), read_split(right, "text"))
    assert result == [
        {"left_lines": [1, 3], "right_lines": [2, 3]},
        {"left_lines": [2], "right_lines": [1]},
    ]


def test_unicode_is_exact_and_unicode_separator_is_not_a_record_boundary(tmp_path):
    left = write(tmp_path, "l", '{"text":"café\u2028x"}'.encode())
    right = write(tmp_path, "r", '{"text":"café\u2028x"}'.encode())
    assert find_matches(read_split(left, "text"), read_split(right, "text"))[0]["left_lines"] == [1]
    different = write(tmp_path, "d", '{"text":"café\u2028x"}'.encode())
    assert find_matches(read_split(left, "text"), read_split(different, "text")) == []


@pytest.mark.parametrize("data", [
    b"{\"text\":\"x\",\"text\":\"y\"}\n", b'{"text":NaN}\n', b'{"text":Infinity}\n',
    b"\n", b'{"text":1}\n', b"[]\n", b"{\"other\":\"x\"}\n", b'{"text":"x"}\n\n',
    b'{"text":"ok"}\nnot-json\n', b'{"text":"ok"}\n\xff',
])
def test_rejects_invalid_records_anywhere(tmp_path, data):
    path = write(tmp_path, "bad", data)
    with pytest.raises(InvalidInput):
        read_split(path, "text")


def test_empty_file_valid_and_one_sided_repeats_are_not_overlap(tmp_path):
    empty = write(tmp_path, "empty", b"")
    repeated = write(tmp_path, "rep", b'{"text":"x"}\n{"text":"x"}\n')
    assert read_split(empty, "text") == []
    assert find_matches(read_split(repeated, "text"), []) == []


def test_unreadable_path_is_invalid(tmp_path):
    with pytest.raises(InvalidInput):
        read_split(tmp_path / "missing", "text")


def test_only_top_level_field_used(tmp_path):
    path = write(tmp_path, "nested", b'{"meta":{"text":"no"},"text":"yes"}')
    assert read_split(path, "text") == [("yes", 1)]

