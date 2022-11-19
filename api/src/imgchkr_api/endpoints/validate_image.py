from typing import Dict, Mapping, Optional, Tuple, cast

import structlog
from celery import Celery, states
from celery.result import AsyncResult
from flask import Flask, Response, jsonify, request

from imgchkr_api.receiver import ImageCheckRequestReceiver


class ValidateImageEndpoint:
    _HTTP_OK = 200
    _HTTP_BAD_REQUEST = 400

    def __init__(
        self,
        celery: Celery,
        receiver: ImageCheckRequestReceiver,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._celery = celery
        self._receiver = receiver
        self._logger = logger

    def submit(self, raw_data: Mapping) -> Tuple[dict, int]:
        log = self._logger.bind(json=raw_data)
        task_id, errors = self._receiver(raw_data)
        if errors:
            log.error('task.invalid', task_id=task_id, errors=errors)
            return {'errors': errors, 'state': 'failed'}, self._HTTP_BAD_REQUEST
        log.info('task.submitted', task_id=task_id)
        return self._format_task_status(task_id), self._HTTP_OK

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
            'state': state,
            **(errors or {}),
        }

    def bind(self, app: Flask) -> None:
        def explicit_submit() -> Tuple[Response, int]:
            data, status_code = self.submit(cast(Mapping, request.json))
            return jsonify(data), status_code

        app.add_url_rule(
            '/assets/image',
            endpoint='validate_image',
            methods=['POST'],
            view_func=explicit_submit,
        )
        app.add_url_rule(
            '/assets/image/<string:task_id>',
            endpoint='task_status',
            methods=['GET'],
            view_func=self.get_task_status,
        )
