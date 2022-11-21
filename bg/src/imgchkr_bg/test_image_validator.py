import unittest
from unittest import mock

from imgchkr_bg.asset import Asset
from imgchkr_bg.asset_downloader import AssetDownloader
from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_checker import ImageChecker
from imgchkr_bg.image_header_checker import ImageHeaderChecker
from imgchkr_bg.image_validator import ImageValidator


class ImageValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._asset_downloader = mock.MagicMock(spec_set=AssetDownloader)
        self._header_checker = mock.Mock(spec_set=ImageHeaderChecker)
        self._header_checker.return_value = {}
        self._image_checker = mock.Mock(spec_set=ImageChecker)
        self._image_checker.return_value = {}
        self._asset = mock.Mock(spec=Asset)
        self._asset.check_exists.return_value = {}
        self._asset.get_size.return_value = 0, {}
        self._asset.get_header.return_value = b'header', {}
        self._asset.get_content.return_value = b'content', {}
        self._asset_downloader.return_value.__enter__.return_value = self._asset
        self._image_validator = ImageValidator(
            asset_downloader=self._asset_downloader,
            header_checker=self._header_checker,
            image_checker=self._image_checker,
        )

    def test_empty_dict_for_good_image(self) -> None:
        result = self._invoke()
        assert result == {}
        self._header_checker.assert_called_once_with(b'header')
        self._image_checker.assert_called_once_with(b'content')

    def test_check_exists_error_proxied(self) -> None:
        self._asset.check_exists.return_value = {'key': 'value'}
        result = self._invoke()
        assert result == {'key': 'value'}
        self._header_checker.assert_not_called()
        self._image_checker.assert_not_called()

    def test_get_size_error_proxied(self) -> None:
        self._asset.get_size.return_value = 0, {'size': 'big'}
        result = self._invoke()
        assert result == {'size': 'big'}
        self._header_checker.assert_called_once_with(b'header')
        self._image_checker.assert_not_called()

    def test_get_size_and_bad_header_error_proxied(self) -> None:
        self._asset.get_size.return_value = 0, {'size': 'big'}
        self._header_checker.return_value = {'image': 'bad'}
        result = self._invoke()
        assert result == {'size': 'big', 'image': 'bad'}
        self._header_checker.assert_called_once_with(b'header')
        self._image_checker.assert_not_called()

    def test_get_content_error_proxied(self) -> None:
        self._asset.get_content.return_value = b'', {'key': 'value'}
        result = self._invoke()
        assert result == {'key': 'value'}
        self._image_checker.assert_not_called()

    def test_image_checker_error_proxied(self) -> None:
        self._image_checker.return_value = {'key': 'value'}
        result = self._invoke()
        assert result == {'key': 'value'}

    def _invoke(self) -> dict:
        return self._image_validator(location_type=LocationType.LOCAL_FILE, path='path')
