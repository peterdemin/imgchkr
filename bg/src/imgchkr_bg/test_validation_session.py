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
            mock.call('validate.started', kwargs=self._kwargs),
            mock.call('validate.ok'),
        ]
