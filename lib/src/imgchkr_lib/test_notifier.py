import unittest
from unittest import mock

import httpx
import structlog

from imgchkr_lib.notifier import Notifier


class NotifierTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._client = mock.Mock(spec_set=httpx.Client)
        self._response = mock.Mock(spec_set=httpx.Response)
        self._client.post.return_value = self._response
        self._logger = mock.Mock(spec_set=structlog.stdlib.BoundLogger)
        self._logger.bind.return_value = self._logger
        self._notifier = Notifier(client=self._client, logger=self._logger)

    def test_successfull_post_returns_empty_error_message(self) -> None:
        result = self._notifier('url', {'key': 'value'})
        assert result == ''
        self._client.post.assert_called_once_with('url', json={'key': 'value'})
        self._response.raise_for_status.assert_called_once_with()
        self._logger.info.assert_called_once_with('notification.sent')

    def test_empty_url_skips_post(self) -> None:
        result = self._notifier('', {'key': 'value'})
        assert result == ''
        self._client.post.assert_not_called()
        self._logger.warning.assert_called_once_with('notification.skipped')

    def test_failed_post_returns_error(self) -> None:
        self._client.post.side_effect = httpx.ConnectError('message')
        result = self._notifier('url', {'key': 'value'})
        assert result == 'Notification failed'
        self._client.post.assert_called_once_with('url', json={'key': 'value'})
        self._logger.exception.assert_called_once_with('notification.failed')

    def test_bad_status_code_returns_error(self) -> None:
        self._response.raise_for_status.side_effect = httpx.HTTPError('not found')
        result = self._notifier('url', {'key': 'value'})
        assert result == 'Notification failed'
        self._client.post.assert_called_once_with('url', json={'key': 'value'})
        self._logger.exception.assert_called_once_with('notification.failed')
