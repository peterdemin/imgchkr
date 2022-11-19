import unittest
from logging import getLogger
from unittest import mock

import structlog

from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.notifier import Notifier
from imgchkr_bg.validation_session import validate_image

LOGGER = getLogger(__name__)


class ValidationSessionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._image_validator = mock.Mock(spec_set=ImageValidator)
        self._image_validator.return_value = {}
        self._notifier = mock.Mock(spec_set=Notifier)
        self._notifier.return_value = ''
        self._logger = mock.Mock(spec_set=structlog.stdlib.BoundLogger)
        self._logger.bind.return_value = self._logger
        self._kwargs = {
            'location': 'local',
            'path': 'path',
            'on_start': 'http://start',
            'on_success': 'http://success',
            'on_failure': 'http://failure',
        }

    def test_successful_validation(self) -> None:
        result = validate_image(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
            task_id='task_id',
            kwargs=self._kwargs,
        )
        assert result == {'id': 'task_id', 'state': 'success'}
        assert self._image_validator.call_args == mock.call(
            location_type=LocationType.LOCAL_FILE, path='path'
        )
        assert self._notifier.call_args_list == [
            mock.call('http://start', {'id': 'task_id', 'state': 'started'}),
            mock.call('http://success', {'id': 'task_id', 'state': 'success'}),
        ]
        assert self._logger.info.call_args_list == [
            mock.call('validation.started', kwargs=self._kwargs),
            mock.call('validation.ok'),
        ]

    def test_validation_continues_with_failing_notifications(self) -> None:
        self._notifier.return_value = 'failed'
        result = validate_image(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
            task_id='task_id',
            kwargs=self._kwargs,
        )
        assert result == {
            'errors': {'notifications': {'on_start': 'failed', 'on_success': 'failed'}},
            'id': 'task_id',
            'state': 'success',
        }
        assert self._image_validator.call_args == mock.call(
            location_type=LocationType.LOCAL_FILE, path='path'
        )
        assert self._notifier.call_args_list == [
            mock.call('http://start', {'id': 'task_id', 'state': 'started'}),
            mock.call(
                'http://success',
                {
                    'id': 'task_id',
                    'state': 'success',
                    'errors': {'notifications': {'on_start': 'failed', 'on_success': 'failed'}},
                },
            ),
        ]
        assert self._logger.info.call_args_list == [
            mock.call('validation.started', kwargs=self._kwargs),
            mock.call('validation.ok'),
        ]

    def test_aborts_on_invalid_arguments(self) -> None:
        kwargs = dict(self._kwargs, on_start='invalid')
        result = validate_image(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
            task_id='task_id',
            kwargs=kwargs,
        )
        assert result == {
            'errors': {'parameters': {'on_start': ['Not a valid URL.']}},
            'id': 'task_id',
            'state': 'failed',
        }
        self._image_validator.assert_not_called()
        self._notifier.assert_not_called()
        self._logger.info.assert_called_once_with('validation.started', kwargs=kwargs)
        self._logger.error.assert_called_once_with(
            'validation.failed', errors={'parameters': {'on_start': ['Not a valid URL.']}}
        )
