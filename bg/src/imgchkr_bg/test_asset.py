import unittest
from unittest import mock

from .asset import Asset
from .base_location_downloader import BaseLocationDownloader


class AssetTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._downloader = mock.Mock(wraps=BaseLocationDownloader())
        self._downloader.errors = {}
        self._asset = Asset(self._downloader)

    def test_check_exists_success(self) -> dict:
        self._downloader.exists.return_value = True
        assert self._asset.check_exists() == {}

    def test_check_exists_passes_error(self) -> dict:
        self._downloader.exists.return_value = False
        self._downloader.errors = self._ERRORS
        assert self._asset.check_exists() == self._ERRORS

    def test_get_size_success(self) -> None:
        self._downloader.fetch_size.return_value = 1
        assert self._asset.get_size() == (1, {})

    def test_get_size_passes_error(self) -> None:
        self._downloader.fetch_size.return_value = 0
        self._downloader.errors = self._ERRORS
        assert self._asset.get_size() == (0, self._ERRORS)

    def test_get_header_success(self) -> None:
        self._downloader.fetch_header.return_value = b'1'
        assert self._asset.get_header() == (b'1', {})

    def test_get_header_passes_error(self) -> None:
        self._downloader.fetch_header.return_value = b''
        self._downloader.errors = self._ERRORS
        assert self._asset.get_header() == (b'', self._ERRORS)

    def test_get_content_success(self) -> None:
        self._downloader.fetch_content.return_value = b'1'
        assert self._asset.get_content() == (b'1', {})

    def test_get_content_passes_error(self) -> None:
        self._downloader.fetch_content.return_value = b''
        self._downloader.errors = self._ERRORS
        assert self._asset.get_content() == (b'', self._ERRORS)

    _ERRORS = {'key': 'value'}
