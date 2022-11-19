FROM python:3.10-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

RUN apk add libmagic

COPY requirements /requirements
RUN pip install -r requirements/background.txt

COPY . /imgchkr
WORKDIR /imgchkr

RUN pip install ./bg

CMD ["celery", "--app", "imgchkr_bg.cli", "worker", "--concurrency=10", "--loglevel=INFO", "-E"]
