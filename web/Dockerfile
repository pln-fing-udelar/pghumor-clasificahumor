FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /usr/src/app
RUN touch README.md
COPY pyproject.toml uv.lock ./
COPY clasificahumor clasificahumor
RUN uv sync --locked
EXPOSE 5000
CMD ["uv", "run", "flask", "run", "-h", "::", "--debug"]
