import os
import unittest
from zlib import adler32

from imgchkr_bg.local_file_reader import LocalFileReader

_HERE = os.path.dirname(__file__)
_TESTDATA = os.path.join(_HERE, 'testdata')


class LocalFileReaderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._local_file_reader = LocalFileReader(os.path.join(_TESTDATA, 'small.jpg'))
        self._missing_file_reader = LocalFileReader(os.path.join(_TESTDATA, 'missing'))

    def test_small_file_read(self) -> None:
        with self._local_file_reader:
            assert not self._local_file_reader.errors
            assert self._local_file_reader.exists()
            assert self._local_file_reader.fetch_size() == 6340
            header = self._local_file_reader.fetch_header()
            assert len(header) == 2048
            assert adler32(header) == 3934882122
            content = self._local_file_reader.fetch_content()
            assert len(content) == 6340
            assert content.startswith(header)
            assert adler32(content) == 2568880604

    def test_missing_file_adds_error(self) -> None:
        with self._missing_file_reader:
            assert self._missing_file_reader.errors == {'open': 'No such file or directory'}
