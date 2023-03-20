from typing import Any, Dict, Mapping, Optional, Tuple, Type, cast

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
            log.error('task.invalid', errors=errors)
            return {'errors': errors, 'state': 'failed'}, self._HTTP_BAD_REQUEST
        log.info('task.submitted', task_id=task_id)
        return self._format_task_status(task_id), self._HTTP_OK

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        async_result = self._get_task(task_id)
        if async_result.state == states.PENDING:
            result = self._format_task_status(task_id)
        elif async_result.state == states.FAILURE:
            result = self._format_task_status(
                task_id, 'failed', errors={'unhandled': repr(async_result.result)}
            )
        else:
            result = cast(Dict, async_result.result)
        self._logger.info('task.status', status=result)
        return result

    def _get_task(self, task_id: str) -> AsyncResult:
        return cast(Type[AsyncResult], self._celery.AsyncResult)(task_id)

    def _format_task_status(
        self, task_id: str, state: str = 'queued', errors: Optional[dict] = None
    ) -> Dict[str, str]:
        return {'id': task_id, 'state': state, **(errors or {})}

    def bind(self, app: Flask) -> None:
        def explicit_submit() -> Tuple[Response, int]:
            data, status_code = self.submit(cast(Mapping, request.json))
            return jsonify(data), status_code

        def explicit_status(task_id) -> Tuple[Response, int]:
            data = self.get_task_status(task_id)
            return jsonify(data), 200

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
            view_func=explicit_status,
        )
