from imgchkr_bg.worker_factory import build_worker

celery = build_worker()


def serve():
    celery.start(['--app', 'imgchkr_bg.cli', 'worker', '--concurrency=1', '--loglevel=INFO', '-E'])


if __name__ == '__main__':
    serve()
