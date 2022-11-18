from typing import Dict

from celery import Celery, states
from flask import Flask, Response, jsonify, request, url_for

from imgchkr_api.receiver import ImageCheckRequestReceiver


class ValidateImageEndpoint:
    def __init__(self, celery: Celery, receiver: ImageCheckRequestReceiver) -> None:
        self._celery = celery
        self._receiver = receiver

    def submit(self) -> Response:
        task_id, errors = self._receiver(request.json)
        if errors:
            return jsonify({'errors': errors, 'state': 'failed'}), 400
        return jsonify(self._format_task_status(task_id))

    def get_task_status(self, task_id: str) -> str:
        async_task = self._celery.AsyncResult(task_id)
        if async_task.state == states.PENDING:
            result = self._format_task_status(task_id)
        elif async_task.state == states.FAILURE:
            result = self._format_task_status(
                task_id, 'failed', errors={'unhandled': repr(async_task.result)}
            )
        else:
            result = async_task.result
        return jsonify(result)

    def _format_task_status(
        self, task_id: str, state: str = 'queued', **kwargs: str
    ) -> Dict[str, str]:
        return {
            'id': task_id,
            'url': url_for('task_status', task_id=task_id),
            'state': state,
            **kwargs,
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
