import os
import unittest

from imgchkr_bg.image_header_checker import ImageHeaderChecker

_HERE = os.path.dirname(__file__)
_TESTDATA = os.path.join(_HERE, 'testdata')


class ImageHeaderCheckerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._image_header_checker = ImageHeaderChecker()

    def test_valid_jpeg_passes(self) -> None:
        with open(os.path.join(_TESTDATA, 'small.jpg'), 'rb') as fobj:
            header = fobj.read(2048)
        result = self._image_header_checker(header)
        assert not result

    def test_empty_file_errors(self) -> None:
        result = self._image_header_checker(b'')
        assert result == {'image': 'Not a JPEG (application/x-empty)'}
