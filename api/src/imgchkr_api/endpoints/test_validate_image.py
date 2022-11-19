import unittest
from unittest import mock

import structlog
from celery import Celery

from imgchkr_api.receiver import ImageCheckRequestReceiver
from imgchkr_api.endpoints.validate_image import ValidateImageEndpoint


class ValidateImageEndpointTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._celery = mock.Mock(spec_set=Celery)
        self._receiver = mock.Mock(spec_set=ImageCheckRequestReceiver)
        self._receiver.return_value = 'id', {}
        self._logger = mock.Mock(spec_set=structlog.stdlib.BoundLogger)
        self._logger.bind.return_value = self._logger
        self._endpoint = ValidateImageEndpoint(
            celery=self._celery,
            receiver=self._receiver,
            logger=self._logger,
        )

    def test_submit_returns_queued_status(self) -> None:
        data, status_code = self._endpoint.submit({'key': 'value'})
        assert status_code == 200
        assert data == {'id': 'id', 'state': 'queued'}
