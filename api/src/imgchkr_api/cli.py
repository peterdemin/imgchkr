from .app import app


def serve():
    app.run(host='0.0.0.0', port=5001)


if __name__ == '__main__':
    serve()
