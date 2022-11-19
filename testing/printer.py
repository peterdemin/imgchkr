import logging
import sys

from flask import Flask, Response, request


class DebugEndpoint:
    def print(self, target: str) -> Response:
        print(f'{target}: {request.json}', file=sys.stderr)
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


def main():
    host, port = '0.0.0.0', 5002
    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.WARNING)
    flask_app = build_app()
    logger.info("Running on %s:%s", host, port)
    flask_app.run(host, port, debug=False)


if __name__ == '__main__':
    main()
else:
    app = build_app()
