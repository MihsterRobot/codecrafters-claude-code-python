import tempfile

import pytest

from app import tools as t


def test_read_returns_file_contents():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('hello')
        temp_path = f.name
    content = t.read({'file_path': temp_path})
    assert content == 'hello'


def test_read_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        t.read({'file_path': 'nonexistent_path'})






