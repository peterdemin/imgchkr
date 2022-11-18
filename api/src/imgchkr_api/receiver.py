from typing import Mapping, Tuple

from imgchkr_api.payload_validator import PayloadValidator
from imgchkr_api.task_sender_interface import TaskSenderInterface


class ImageCheckRequestReceiver:
    def __init__(
        self,
        payload_validator: PayloadValidator,
        task_sender: TaskSenderInterface,
    ) -> None:
        self._validator = payload_validator
        self._task_sender = task_sender

    def __call__(self, request_data: Mapping) -> Tuple[str, dict]:
        try:
            payload = self._validator(request_data)
        except self._validator.Error as exc:
            return '', exc.messages_dict
        return (
            self._task_sender(
                location=payload['asset_path']['location'],
                path=payload['asset_path']['path'],
                on_start=payload['notifications']['on_start'],
                on_success=payload['notifications']['on_success'],
                on_failure=payload['notifications']['on_failure'],
            ),
            {},
        )
