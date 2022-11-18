import unittest
from unittest import mock

from imgchkr_api.payload_validator import PayloadValidator
from imgchkr_api.receiver import ImageCheckRequestReceiver
from imgchkr_api.task_sender_interface import TaskSenderInterface


class ImageCheckRequestReceiverTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._payload_validator = mock.Mock(spec_set=PayloadValidator, Error=PayloadValidator.Error)
        self._task_sender = mock.Mock(spec_set=TaskSenderInterface)
        self._image_check_request_receiver = ImageCheckRequestReceiver(
            payload_validator=self._payload_validator,
            task_sender=self._task_sender,
        )
        self._payload_validator.return_value = self._VALID_PAYLOAD
        self._task_sender.return_value = 'task_id'

    def test_receive_sample_request(self) -> str:
        task_id, errors = self._image_check_request_receiver({'key': 'value'})
        assert task_id == 'task_id'
        assert errors == {}

    def test_validation_failure(self) -> str:
        self._payload_validator.side_effect = self._payload_validator.Error({'key': 'bad'})
        task_id, errors = self._image_check_request_receiver({'key': 'value'})
        assert task_id == ''
        assert errors == {'key': 'bad'}

    _VALID_PAYLOAD = {
        'asset_path': {
            'location': 'location',
            'path': 'path',
        },
        'notifications': {
            'on_start': 'on_start',
            'on_success': 'on_success',
            'on_failure': 'on_failure',
        },
    }
