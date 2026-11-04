FROM python:3.15-slim

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1

# Because of the caching:
ENV UV_LINK_MODE=copy

RUN \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-default-groups --locked --no-install-project

COPY pyproject.toml uv.lock ./
COPY src/clasificahumor src/clasificahumor

RUN \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-default-groups --locked

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:80/healthz')"]

CMD ["sh", "-c", "exec uvicorn clasificahumor.__main__:app --host :: --port 80 --workers \"$(($(nproc) + 1))\""]
