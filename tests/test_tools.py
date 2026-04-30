import tempfile

import pytest

from app import tools as t


def test_read_returns_file_contents():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('grok')
        temp_path = f.name
    content = t.read({'file_path': temp_path})
    assert content == 'grok'


def test_read_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        t.read({'file_path': 'nonexistent_dir/nonexistent_path'})


def test_write_returns_success_message():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name
    result = t.write({'file_path': temp_path, 'content': 'krypto'})
    assert result == 'Write successful'


def test_write_contains_correct_file_content():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name

    t.write({'file_path': temp_path, 'content': 'foobar'})
    content = t.read({'file_path': temp_path})
    assert content == 'foobar'


def test_write_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        t.write({'file_path': 'nonexistent_dir/nonexistent_path', 'content': 'marsh'})


def test_bash_returns_stdout():
    result = t.bash({'command': 'echo hello'})
    assert result == 'hello\n'


def test_bash_returns_stderr():
    result = t.bash({'command': 'nonexistent_cmd BIOS'})
    assert result != ''


def test_get_tool_specs_returns_valid_structure():
    result = t.get_tool_specs()
    assert len(result) == 3
    for spec in result:
        assert 'type' in spec
        assert 'function' in spec
