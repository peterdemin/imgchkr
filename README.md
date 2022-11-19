# Image Validator

## Getting Started

Image validator checks that an image file is valid:

- The file is reachable by the server.
- The file size is under 10 MB.
- The file is a JPEG image.
- The image has width and height not greater than 1000px.

During validation, progress is reported through notification URLs.
If any URL is invalid or not provided, submission is rejected.

Valid but unreachable URLs are reported back, but do not block image validation.

## Usage

API accepts JSON POST payloads at `/assets/image` path.
All parameters are required:

- `assetPath`:
    - `location` - location type, currently only "local" is supported.
    - `path` - local filesystem path, (e.g., "images/small.jpg").
- `notifications`:
    - `onStart` - URL to be notified when image validation begins.
    - `onSuccess` - URL to be notified when image validation finishes successfully - no issues found.
    - `onFailure` - URL to be notified when issues are found.

Example request:

```
curl http://imgchkr/assets/image \
    -XPOST -H "content-type: application/json" \
    -d '{"assetPath": {"location":"local","path":"images/small.jpg"}, \
        "notifications":{ \
            "onStart":"http://callback/print/onStart", \
            "onSuccess":"http://callback/print/onSuccess", \
            "onFailure":"http://callback/print/onFailure"}}'
```

Example response:

```
{
  "id": "497ea3c4-180a-4292-8cc2-0aa1d500d80f",
  "state": "queued"
}
```

To fetch status of queued submission on demand,
put `id` value in this GET request:

```
curl http://127.0.0.1:5001/assets/image/<ID>
```

For example:

```curl http://127.0.0.1:5001/assets/image/497ea3c4-180a-4292-8cc2-0aa1d500d80f
{
  "id": "497ea3c4-180a-4292-8cc2-0aa1d500d80f",
  "state": "success"
}
```


## Running Tests

Tests can be run inside of Docker containers:

```
make test  # unit tests
make test-e2e  # end-to-end tests
```

Or in the activate virtualenv:

```
make install coverage lint
```

## Running service

Service can be run inside of Docker containers:

```
make server
make dev-server  # Adds extra containers for local development
```

Or in the activate virtualenv:

```
make install
make run_api    # Run API in foreground mode
make run_bg     # Run background worker in foreground mode
make run_redis  # Runs a Dockerized redis
```

## Architecture

Service uses two-tier architecture:

1. JSON HTTP API accepts image asset submissions and pushes them to background processing queue.
   It responds back with task ID, that can be used to check the job status later.
2. Background worker processing image submissions from a queue.
   During processing it uses web hooks to notify about progress for the following events: started, success, and failed. 

Services use external queue broker (RabbitMQ and Redis are supported) for interaction.


## Security Concerns


## Scalability


How would you scale this implementation?


## Monitoring


Thoughts on the key metrics you would track to understand the health of this service

## Dependency management

This project uses [pip-compile-multi](https://pypi.org/project/pip-compile-multi/) for hard-pinning dependencies versions.
Please see its documentation for usage instructions.
In short, `requirements/base.in` contains the list of direct requirements with occasional version constraints (like `Django<2`)
and `requirements/base.txt` is automatically generated from it by adding recursive tree of dependencies with fixed versions.
The same goes for other requirements files.

To upgrade dependency versions, run `make upgrade`.

To add a new dependency without upgrade, add it to `requirements/<appropriate-env>.in` and run `make lock`.

For installation always use `.txt` files. For example, command `pip install -r requirements/local.txt`
will install all dependencies for this project.
Another useful command is `make sync`, it install all requirements and uninstalls packages
from your virtualenv that aren't listed.

## Future work

Some ideas on how you would tackle any missing requirements.
Ideas on how to make the service amenable to accepting more data types for validation.
Anything else you can think of.


## Docker Flask Celery Redis

### Build & Launch

```bash
docker-compose up -d --build
```

### Enable hot code reload

```
docker-compose -f docker-compose.development.yml up --build
```

This will expose the Flask application's endpoints on port `5001` as well as
a [Flower](https://github.com/mher/flower) server for monitoring workers on port `5555`

To add more workers:
```bash
docker-compose up -d --scale worker=5 --no-recreate
```

To shut down:

```bash
docker-compose down
```
