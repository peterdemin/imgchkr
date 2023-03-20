FROM --platform=linux/amd64 python:3.10-alpine AS build-image

RUN python -m venv /opt/venv
# Activate virtualenv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements /requirements
RUN pip install -r requirements/api.txt

COPY api /pkg
WORKDIR /pkg
RUN pip install .

# 8< - - - - - - - - - - - - - - - - - - - - - - - -

FROM python:3.10-alpine AS app-image

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true
# Activate virtualenv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=build-image /opt/venv /opt/venv

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "3", "imgchkr_api.cli:app"]
