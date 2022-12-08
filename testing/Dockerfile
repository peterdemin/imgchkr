FROM python:3.10-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

RUN apk add libmagic make

COPY requirements /requirements
RUN pip install -r requirements/ci.txt

WORKDIR /imgchkr
COPY api api
COPY bg bg
COPY lib lib

EXPOSE 5002
EXPOSE 5555

RUN pip install ./api ./bg ./lib

CMD ["/bin/sh", "testing/start.sh"]
