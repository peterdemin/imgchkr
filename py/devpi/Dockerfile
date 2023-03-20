FROM python:3.10 AS build-image

RUN python -m venv /opt/venv
# Activate virtualenv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements/devpi.txt /requirements/devpi.txt
RUN pip install -r /requirements/devpi.txt

FROM python:3.10 AS app-image

# Copy and activate virtualenv
COPY --from=build-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Add entrypoint
COPY devpi/devpi-client /usr/local/bin/
COPY devpi/entrypoint.sh /
ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]

# Set default server root
ENV DEVPI_SERVER_ROOT=/devpi
EXPOSE 3141
