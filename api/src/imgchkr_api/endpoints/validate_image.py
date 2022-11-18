from typing import Dict, Mapping, Optional, Tuple, Union, cast

from celery import Celery, states
from celery.result import AsyncResult
from flask import Flask, Response, jsonify, request, url_for

from imgchkr_api.receiver import ImageCheckRequestReceiver


class ValidateImageEndpoint:
    def __init__(self, celery: Celery, receiver: ImageCheckRequestReceiver) -> None:
        self._celery = celery
        self._receiver = receiver

    def submit(self) -> Union[Response, Tuple[Response, int]]:
        task_id, errors = self._receiver(cast(Mapping, request.json))
        if errors:
            return jsonify({'errors': errors, 'state': 'failed'}), 400
        return jsonify(self._format_task_status(task_id))

    def get_task_status(self, task_id: str) -> Response:
        async_task: AsyncResult = AsyncResult(task_id, app=self._celery)
        if async_task.state == states.PENDING:
            result = self._format_task_status(task_id)
        elif async_task.state == states.FAILURE:
            result = self._format_task_status(
                task_id, 'failed', errors={'unhandled': repr(async_task.result)}
            )
        else:
            result = cast(Dict, async_task.result)
        return jsonify(result)

    def _format_task_status(
        self, task_id: str, state: str = 'queued', errors: Optional[dict] = None
    ) -> Dict[str, str]:
        return {
            'id': task_id,
            'url': url_for('task_status', task_id=task_id),
            'state': state,
            **(errors or {}),
        }

    def bind(self, app: Flask) -> None:
        app.add_url_rule(
            '/assets/image',
            endpoint='validate_image',
            methods=['POST'],
            view_func=self.submit,
        )
        app.add_url_rule(
            '/check/<string:task_id>',
            endpoint='task_status',
            methods=['GET'],
            view_func=self.get_task_status,
        )
