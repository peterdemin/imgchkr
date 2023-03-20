import unittest
from unittest import mock

import structlog
from celery import Celery, states
from celery.result import AsyncResult
from flask import Flask

from imgchkr_api.endpoints.validate_image import ValidateImageEndpoint
from imgchkr_api.receiver import ImageCheckRequestReceiver


class ValidateImageEndpointTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._async_result = mock.Mock(spec_set=AsyncResult)
        self._celery = mock.Mock(spec_set=Celery)
        self._celery.AsyncResult.return_value = self._async_result
        self._receiver = mock.Mock(spec_set=ImageCheckRequestReceiver)
        self._receiver.return_value = 'id', {}
        self._logger = mock.Mock(spec_set=structlog.stdlib.BoundLogger)
        self._logger.bind.return_value = self._logger
        self._flask = mock.Mock(spec_set=Flask)
        self._endpoint = ValidateImageEndpoint(
            celery=self._celery,
            receiver=self._receiver,
            logger=self._logger,
        )

    def test_submit_returns_queued_status(self) -> None:
        data, status_code = self._endpoint.submit({'key': 'value'})
        assert status_code == 200
        assert data == {'id': 'id', 'state': 'queued'}
        assert self._receiver.call_args_list == [mock.call({'key': 'value'})]
        self._logger.info.assert_called_once_with('task.submitted', task_id='id')

    def test_validation_error_returned_and_logged(self) -> None:
        self._receiver.return_value = '', {'err': 'bad'}
        data, status_code = self._endpoint.submit({'key': 'value'})
        assert status_code == 400
        assert data == {'state': 'failed', 'errors': {'err': 'bad'}}
        self._logger.error.assert_called_once_with('task.invalid', errors={'err': 'bad'})

    def test_get_status_formats_queued(self) -> None:
        self._async_result.state = states.PENDING
        data = self._endpoint.get_task_status('id')
        assert data == {'id': 'id', 'state': 'queued'}
        self._logger.info.assert_called_once_with(
            'task.status', status={'id': 'id', 'state': 'queued'}
        )

    def test_get_status_formats_success(self) -> None:
        self._async_result.state = states.SUCCESS
        self._async_result.result = {'key': 'value'}
        data = self._endpoint.get_task_status('id')
        assert data == {'key': 'value'}
        self._logger.info.assert_called_once_with('task.status', status={'key': 'value'})

    def test_get_status_formats_failure(self) -> None:
        self._async_result.state = states.FAILURE
        self._async_result.result = 'bad stuff'
        data = self._endpoint.get_task_status('id')
        assert data == {'id': 'id', 'state': 'failed', 'unhandled': "'bad stuff'"}
        self._logger.info.assert_called_once_with(
            'task.status', status={'id': 'id', 'state': 'failed', 'unhandled': "'bad stuff'"}
        )

    def test_bind_routes(self) -> None:
        self._endpoint.bind(self._flask)
        assert self._flask.add_url_rule.call_args_list == [
            mock.call(
                '/assets/image',
                endpoint='validate_image',
                methods=['POST'],
                view_func=mock.ANY,
            ),
            mock.call(
                '/assets/image/<string:task_id>',
                endpoint='task_status',
                methods=['GET'],
                view_func=mock.ANY,
            ),
        ]
