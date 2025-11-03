FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /usr/src/app
COPY pyproject.toml uv.lock README.md ./
COPY clasificahumor clasificahumor
RUN uv sync --locked
EXPOSE 5000
CMD ["uv", "run", "flask", "run", "-h", "::", "--debug"]
