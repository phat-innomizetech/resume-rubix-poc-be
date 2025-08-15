# FastAPI Starter

This is a starter project for building a FastAPI application using Python 3.x. It includes:

- A FastAPI app with liveness and readiness endpoints.
- Integration with Python venv and VS Code Dev Container.
- A Dockerfile for containerized deployment.
- Configuration for code formatting (Black and isort).
- Automatic Swagger documentation available at `/docs`.

## Requirements

- [Docker](https://www.docker.com/) v28 installed.
- [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Getting Started

### Develop with uv and Virtual Environment

By default, the dependencies are managed with uv, go there and install it.

```bash
uv venv

# Then you can activate the virtual environment with:
source .venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

Install dependencies

```bash
uv sync
uv run python -m spacy download en_core_web_sm
```

Run the application:

```bash
fastapi run --reload src/rubix/main.py
```

Access the Swagger documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Develop with Docker Compose

A Docker compose configuration is also provided to demonstrate best practices for developing using the container with Docker compose. Docker compose is more complex than using `docker run`, but has more robust support for various workflows.

To build and run the Then, check out [`http://localhost:8000`](http://localhost:8000) to see the FastAPI application.
using Docker compose:

```
docker compose up --watch
```

### Run with Docker

Build the Docker image:

```bash
docker build -t rubix .
```

Run the Docker container:

```bash
docker run -p 8000:8000 --env-file .env rubix
```

Access the API at: [http://localhost/](http://localhost/). Swagger docs are available at [http://localhost/docs](http://localhost/docs)

A [`run.sh`](./run.sh) utility is provided for quickly building the image and starting a container.
This script demonstrates best practices for developing using the container, using bind mounts for the project and virtual environment directories.

To build and run the API in the container using `docker run`:

```console
$ ./run.sh
```

Then, check out [`http://localhost:8000`](http://localhost:8000) to see the FastAPI application.

## Contribution

1. Open an issue on GitHub to describe whether this is a bug, a new feature, or any other type of contribution.
2. Make your changes and submit a pull request (PR) for review.
3. Request others to review your changes.
4. Once approved, merge the changes and share them so others can update and potentially integrate them into their services.
