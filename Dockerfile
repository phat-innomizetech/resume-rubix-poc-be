# First, build the application in the `/app` directory
FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Set environment variables for uv configuration
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_INSTALL_DIR=/python \
    UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.12

# Set the working directory for the application
WORKDIR /app

# Install dependencies using uv.
# Using --mount with type=cache for caching, and type=bind to use 
# the local uv.lock and pyproject.toml files.ß
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable --no-dev

# Copy the entire project into the builder image
ADD . /app

# Re-sync to include changes from the copied source code
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --no-dev

# Stage 2: Production Image
FROM python:3.12-slim

# Create a non-root user "app" for security purposes
RUN groupadd -r app && useradd --no-log-init -r -g app app

# Copy the Python version
COPY --from=builder --chown=app:app /python /python

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Set the working directory in the final image
WORKDIR /app

# Switch to the non-root user
USER app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI application by default
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "src/rubix/main.py"]