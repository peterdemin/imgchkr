FROM python:3.10-alpine AS build-image

RUN python -m venv /opt/venv
# Activate virtualenv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements /requirements
RUN pip install -r requirements/background.txt

COPY bg /bg
COPY lib /deps
RUN pip install ./bg ./deps

# 8< - - - - - - - - - - - - - - - - - - - - - - - -

FROM python:3.10-alpine AS app-image

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
# Activate virtualenv
ENV PATH="/opt/venv/bin:$PATH"

RUN apk add libmagic

COPY --from=build-image /opt/venv /opt/venv

CMD ["celery", "--app", "imgchkr_bg.cli", "worker", \
     "--concurrency=10", "--loglevel=INFO", "-E"]
