FROM python:3.10-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true

COPY requirements /requirements
RUN pip install -r requirements/api.txt

COPY . /imgchkr
WORKDIR /imgchkr

RUN pip install ./api

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "3", "imgchkr_api.cli:app"]
