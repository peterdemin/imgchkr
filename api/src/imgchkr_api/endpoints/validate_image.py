from typing import Dict, Mapping, Optional, Tuple, Union, cast

import structlog
from celery import Celery, states
from celery.result import AsyncResult
from flask import Flask, Response, jsonify, request, url_for

from imgchkr_api.receiver import ImageCheckRequestReceiver


class ValidateImageEndpoint:
    def __init__(
        self,
        celery: Celery,
        receiver: ImageCheckRequestReceiver,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._celery = celery
        self._receiver = receiver
        self._logger = logger

    def submit(self) -> Union[Response, Tuple[Response, int]]:
        raw_data = cast(Mapping, request.json)
        log = self._logger.bind(json=raw_data)
        task_id, errors = self._receiver(raw_data)
        if errors:
            log.error('task.invalid', task_id=task_id, errors=errors)
            return jsonify({'errors': errors, 'state': 'failed'}), 400
        log.info('task.submitted', task_id=task_id)
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
        self._logger.error('task.status', status=result)
        return jsonify(result)

    def _format_task_status(
        self, task_id: str, state: str = 'queued', errors: Optional[dict] = None
    ) -> Dict[str, str]:
        return {
            'id': task_id,
            'url': url_for('task_status', task_id=task_id, external=True),
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
