FROM debian:12-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv
ENV PATH="/venv/bin:/bin/uv:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Build-env stage
FROM build AS build-env
WORKDIR /app

COPY ./src/pyproject.toml ./src/uv.lock ./

RUN uv pip install -r pyproject.toml --target /packages

# Final stage with distroless image
FROM gcr.io/distroless/python3-debian12
USER 1001:1001
ENV PYTHONPATH=/packages
WORKDIR /app

COPY --from=build-env /packages /packages
COPY /src /app

EXPOSE 10000
CMD ["standalone.py"]