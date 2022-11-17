from celery.exceptions import TimeoutError as CeleryTimeoutError
from flask import Response, jsonify, url_for, request

from .app import app
from .worker import celery


@app.route('/assets/image', methods=['POST'])
def validate_image() -> str:
    content = request.json
    task = celery.send_task('tasks.validate_image', kwargs=kwargs)
    url = url_for('check_task', task_id=task.id)
    return jsonify({'id': task.id, 'url': url})


@app.route('/add/<int:param1>/<int:param2>')
def add(param1: int, param2: int) -> str:
    task = celery.send_task('tasks.add', args=[param1, param2], kwargs={})
    url = url_for('check_task', task_id=task.id)
    return jsonify({'id': task.id, 'url': url})


@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    result = celery.AsyncResult(task_id)
    return jsonify({'result': result.result, 'status': result.state})


@app.route('/health')
def health_check() -> Response:
    return jsonify("ok")


@app.route('/deep_health')
def deep_health_check() -> Response:
    task = celery.send_task('tasks.health')
    try:
        result = task.get(timeout=5)
    except CeleryTimeoutError:
        result = 'timeout'
    return jsonify({'bg': result})
