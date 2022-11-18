import os
import unittest

from .image_checker import ImageChecker

_HERE = os.path.dirname(__file__)
_TESTDATA = os.path.join(_HERE, 'testdata')


class ImageCheckerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._image_checker = ImageChecker()

    def test_valid_jpeg_passes(self) -> None:
        result = self._image_checker(self._read_jpeg('small'))
        assert not result

    def test_corrupted_jpeg_fails(self) -> None:
        result = self._image_checker(self._read_jpeg('corrupted'))
        assert result == {'image': 'broken data stream when reading image file'}

    def _read_jpeg(self, label: str) -> bytes:
        with open(os.path.join(_TESTDATA, f'{label}.jpg'), 'rb') as fobj:
            return fobj.read()
