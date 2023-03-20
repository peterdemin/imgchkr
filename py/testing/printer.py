from __future__ import annotations
import json
import logging
import subprocess
import sys
import time
from typing import Optional, List, TextIO, cast
import queue
import threading
import httpx
from flask import Flask, Response, request

HOST, PORT = '0.0.0.0', 5002
HEALTH = f'http://127.0.0.1:{PORT}/health'


class DebugEndpoint:
    def print(self, target: str) -> Response:
        print(f'{target}: {json.dumps(request.json)}', file=sys.stderr)
        return Response()

    def health(self) -> str:
        return "ok"

    def bind(self, flask_app: Flask) -> None:
        flask_app.add_url_rule(
            '/print/<target>',
            endpoint='print',
            methods=['POST'],
            view_func=self.print,
        )
        flask_app.add_url_rule(
            '/health',
            endpoint='health',
            methods=['GET'],
            view_func=self.health,
        )


def build_app() -> Flask:
    flask_app = Flask(__name__)
    DebugEndpoint().bind(flask_app)
    return flask_app


class SubprocessPrinter:
    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen] = None
        self._queue: queue.Queue[str] = queue.Queue()
        self._thread = threading.Thread(target=self._enqueue_output)

    def __enter__(self) -> 'SubprocessPrinter':
        self._proc = subprocess.Popen(
            [sys.executable, '-u', __file__],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
        )
        for _ in range(5):
            time.sleep(0.5)
            try:
                response = httpx.get(HEALTH)
                response.raise_for_status()
                break
            except httpx.HTTPError:
                pass
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.kill()

    def flush_output(self) -> List[str]:
        result = []
        while not self._queue.empty():
            result.append(self._queue.get_nowait())
        return result

    def kill(self) -> None:
        if self._proc:
            self._proc.kill()
            self._thread.join(3)
            self._proc = None

    def _enqueue_output(self) -> None:
        assert self._proc
        stderr_pipe = cast(TextIO, self._proc.stderr)
        for line in iter(stderr_pipe.readline, ''):
            self._queue.put(line.strip())


def main():
    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.WARNING)
    flask_app = build_app()
    logger.info("Running on %s:%s", HOST, PORT)
    flask_app.run(HOST, PORT, debug=False)


if __name__ == '__main__':
    main()
