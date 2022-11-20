# Image Validator

## Getting Started

Image validator checks that an image file is valid:

- The file is reachable by the server.
- The file size is under 10 MB.
- The file is a JPEG image.
- The image has a width and height not greater than 1000px.

During validation, progress is reported through notification URLs.
If any URL is invalid or not provided, the submission is rejected.

Valid but unreachable URLs are reported back but do not block image validation.

## Usage

API accepts JSON POST payloads at the `/assets/image` path.
All parameters are required:

- `assetPath`:
    - `location` - location type, currently only "local" is supported.
    - `path` - local filesystem path (e.g., "images/small.jpg").
- `notifications`:
    - `onStart` - URL to be notified when image validation begins.
    - `onSuccess` - URL to be notified when image validation finishes successfully - no issues found.
    - `onFailure` - URL to be notified when issues are found.

Example request:

```bash
curl http://imgchkr/assets/image \
    -XPOST -H "content-type: application/json" \
    -d '{"assetPath": {"location":"local","path":"images/small.jpg"}, \
        "notifications":{ \
            "onStart":"http://callback/print/onStart", \
            "onSuccess":"http://callback/print/onSuccess", \
            "onFailure":"http://callback/print/onFailure"}}'
```

Example response:

```json
{
  "id": "497ea3c4-180a-4292-8cc2-0aa1d500d80f",
  "state": "queued"
}
```

To fetch the status of queued submissions on demand,
put `id` value in this GET request:

```bash
curl http://127.0.0.1:5001/assets/image/<ID>
```

For example:

```bash
curl http://127.0.0.1:5001/assets/image/497ea3c4-180a-4292-8cc2-0aa1d500d80f
{
  "id": "497ea3c4-180a-4292-8cc2-0aa1d500d80f",
  "state": "success"
}
```

Service sends notifications to configured URLs. Here're a few examples:

```
onStart: {"id": "00000000-0000-0000-0000-000000000000", "state": "started"}

onSuccess: {"id": "00000000-0000-0000-0000-000000000000", "state": "success"}

onFailure: {"id": "00000000-0000-0000-0000-000000000000", "state": "failed",
            "errors": {"image": ["Image width exceeds maximum (1800/1000)",
                       "Image height exceeds maximum (1200/1000)"]}}
```

## Running Tests

Tests can be run inside Docker containers:

```bash
make test      # unit tests
make test-e2e  # end-to-end tests
```

Or in the active virtualenv:

```bash
make install coverage lint
```

## Running service

Service can be run inside Docker containers:

```bash
make server
make dev-server  # Adds extra containers for local development
```

Or in the activate virtualenv:

```bash
make install
make run_api    # Run API in foreground mode
make run_bg     # Run background worker in foreground mode
make run_redis  # Runs a Dockerized Redis
```

When running services locally, you can run end-to-end tests using the command:

```bash
make local-e2e
```

Dev server launches Flower for queue monitoring at http://127.0.0.1:5555.

To add more workers:

```bash
docker-compose up -d --scale worker=5 --no-recreate
```

To shut down:

```bash
docker-compose down
```

## Architecture

Service uses two-tier architecture:

1. JSON HTTP API accepts image asset submissions and pushes them to the background processing queue.
   It responds with a task ID that can be used to check the job status later.
2. Background worker picks up image submissions from a queue.
   During processing, it uses webhooks to notify about progress for the following events: started, success, and failed. 

Services use an external queue broker (RabbitMQ and Redis are supported) for interaction.


## Security Concerns

The service can be used only internally and doesn't have many security features.
If this service is to be exposed to untrusted parties, the following aspects can be improved:

1. **Caller authentication**. Currently, the service accepts image asset submissions without verifying the authenticity of a caller.
   This can be improved by adding token authentication.
2. **Call signature**. HMAC request signature can protect against replay attacks and leaked tokens.
3. **Notifications security**. Same authentication and signature techniques can be applied to notification calls.
4. **Allowed domains for notification URLs**. Service attempts to deliver notifications to any specified URL,
   which might cause a DoS threat to other services. Allowed domains could be set up per-consumer or globally for the cluster.
5. **Allowed directories for image paths**. Even though the caller can't see the file data, this service exposes what files are present on the target host. A check to look only inside the target image directory can mitigate this.

## Scalability

API and background workers can be scaled independently using different signals.
API service is meant to be deployed behind a load balancer.
Background workers pick tasks from a shared queue.

Response latency and CPU load can be used to scale the number of API instances.
Queue length can be a signal to scale the number of background workers.

## Multitenant Fairness

If the service is deployed in a multi-tenant environment, it would need
to have a queue-sharding logic. One consumer can overload the system
and cause degraded performance for all other clients.

## Monitoring

Service uses structlog for both API and background worker, which simplifies ingestion in log aggregation tools,
such as ELK or Graylog.

In addition to event logging, API exposes `/metrics` endpoint for integration with Prometheus (Grafana).

Background worker metrics can be exposed using Celery's built-in features through a separate Docker container.

Alerts need to cover the following:

- Non-200 status codes in the API responses.
- API P90 latency threshold.
- API and worker CPU usage utilization.
- Worker RAM utilization.
- Ratio of success to failure in image validation.

## Dependency management

This project uses [pip-compile-multi](https://pypi.org/project/pip-compile-multi/) for hard-pinning dependencies versions.
Please see its documentation for usage instructions.
In short, `requirements/base.in` contains the list of direct requirements with occasional version constraints (like `Django<2`)
and `requirements/base.txt` is automatically generated by adding a recursive tree of dependencies with fixed versions.
The same goes for other requirements files.

To upgrade dependency versions, run `make upgrade`.

To add a new dependency without an upgrade, add it to `requirements/<appropriate-env>.in` and run `make lock`.

For installation, always use `.txt` files. For example, command `pip install -r requirements/local.txt`
will install all dependencies for this project.
Another useful command is `make sync`. It installs all requirements and uninstalls packages
from your virtualenv that aren't listed.

## Future work

Product quality can be improved with the following tasks:

1. Address security concerns from above.
2. Extract common infrastructure to reusable libraries.
3. Enforce contracts between API service and background workers.
4. Add support for other image formats (PNG, GIF, etc.).
5. Allow clients to supply unique image IDs, so they don't have to track task IDs generated by this service.
6. Alternatively, include assetPath in notifications.
7. Add retries for background tasks.
8. Add retries for notifications.
9. Add rate limit.
10. Add support for HTTPS and SFTP location types.
