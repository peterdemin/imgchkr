import sys
from flask import Flask, Response, request


class DebugEndpoint:

    def print(self, target: str) -> Response:
        print(f'{target}: {request.json}', file=sys.stderr)
        return Response()

    def bind(self, flask: Flask) -> None:
        flask.add_url_rule(
            '/print/<target>',
            endpoint='print',
            methods=['POST'],
            view_func=self.print,
        )


def build_app() -> Flask:
    flask = Flask(__name__)
    DebugEndpoint().bind(flask)
    return flask


app = build_app()


if __name__ == '__main__':
    app.run('0.0.0.0', 5002)
