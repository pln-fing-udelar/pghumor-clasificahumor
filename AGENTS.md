# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

A crowd-annotation web app for humor research (ClasificaHumor / HAHA competitions).
Users classify Spanish tweets as humorous or not humorous, rate their funniness (1 to 5 stars), and flag offensive content.
The system tracks sessions and incorporates test tweets to evaluate annotator quality.

## Architecture

### Core Components

**Database Layer** (`web/src/clasificahumor/database.py`):
- MySQL backend with SQLAlchemy (`asyncmy` in production; `aiosqlite` in tests)
- Tables: `accounts`, `tweets`, `votes`, `prolific`
- Vote choices: `"1"` to `"5"` (degrees of funniness), `"x"` (not humorous), `"n"` (skip)
- Prioritizes unseen tweets with fewer votes; pads with random tweets if necessary

**Web App** (`web/src/clasificahumor/__main__.py`):
- Main routes: `/tweets` (get batch of tweets to annotate), `/vote` (submit classification), `/stats` (view annotation statistics), `/prolific/consent`, `/prolific/finish`
- Cookie-based session tracking (`id`) and Prolific support (`PROLIFIC_PID`)

**Extraction & Analysis** (`web/src/extraction/` and `web/src/analysis/`):
- `extraction/`: Scripts for downloading and ingesting tweets from Twitter streams and humorous accounts
- `analysis/`: Computes inter-annotator agreement (Krippendorff's alpha) across annotations

## Development Commands

### Setup and Run

```bash
# Start services with Docker Compose
docker compose up

# Run locally with uv
cd web/
uv run --env-file ../.env uvicorn clasificahumor.__main__:app --host :: --port 5000 --reload
```

### Code Quality & Testing

```bash
cd web/
uv run ruff check --fix
uv run ruff format
uv run ty check
uv run pytest --cov-fail-under=90 --cov-report=term-missing
```

Configuration in `pyproject.toml`: Python `>=3.15` (using PEP 810 `lazy import` checked by Ruff `TID255`), line length 120.

## Important Details

- **Database name**: `pghumor`
- **Python tool**: `uv` for dependency management (Python `>=3.15`)
- **All scripts** use shebang: `#!/usr/bin/env -S uv run --script --extra scripts --env-file ../.env`
- **Related repo**: [mwahaha-vote-webapp](https://github.com/pln-fing-udelar/mwahaha-vote-webapp) (battle-based pairwise annotation sibling project)
