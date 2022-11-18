from imgchkr_api.app_factory import build_app

app = build_app()


def serve():
    app.run(host='0.0.0.0', port=5001)


if __name__ == '__main__':
    serve()
