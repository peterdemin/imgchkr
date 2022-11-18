from flask import Flask, Response, request


class DebugEndpoint:

    def print(self, target: str) -> Response:
        print(f'{target}: {request.json}')
        return Response()

    def bind(self, app: Flask) -> None:
        app.add_url_rule(
            '/print/<target>',
            endpoint='print',
            methods=['POST'],
            view_func=self.print,
        )
