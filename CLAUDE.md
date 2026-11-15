# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Early-stage FastAPI shop backend. PostgreSQL (pgvector) via async SQLAlchemy; there are no tests and no lint/format config yet. Dependencies are managed with **uv** (`pyproject.toml` + `uv.lock`, venv in `.venv`). Python is **3.12** (`requires-python = ">=3.12"`, pinned in `.python-version`).

## Commands

```bash
uv sync                      # install dependencies into .venv
uv run fastapi dev           # dev server with reload; entrypoint comes from [tool.fastapi] in pyproject.toml (app.main:app)
uv run fastapi run           # production-style server
uv add <pkg>                 # add a dependency (updates pyproject.toml and uv.lock)
docker compose up -d         # start PostgreSQL (pgvector/pgvector:pg18) on localhost:5432
cd scripts && psql "postgresql://postgres:p%40ssword@localhost:5432/fastapi-shop" -f import_products.sql   # create + load products table
```

Config is read by pydantic-settings from env vars / `.env` (gitignored; copy `.env.example`). `POSTGRES_PASSWORD` and `SECRET_KEY` are required.

Interactive API docs are at `http://127.0.0.1:8000/docs` while the server runs.

Ruff has been used (there is a `.ruff_cache`), but it is not a project dependency and has no config. Run it with `uvx ruff check .` / `uvx ruff format .`.

## Architecture

- `app/main.py` holds the `FastAPI()` instance that gets served (`app.main:app`) and mounts feature routers with `app.include_router(...)`. Its `lifespan` runs `SELECT 1` at startup (app fails fast if the DB is down) and disposes the engine on shutdown.
- `app/core/config.py`: `Settings(BaseSettings)` singleton `settings`. `database_url` is built with `sqlalchemy.URL.create` so special chars in the password (e.g. `@`) are escaped — don't build the URL by string formatting.
- `app/db/session.py`: async engine (`postgresql+asyncpg`), `SessionLocal`, `Base(DeclarativeBase)`, and `SessionDep` (`Annotated[AsyncSession, Depends(get_session)]`) for routes.
- `app/models/`: ORM models. `Product` maps the `products` table, which is created by `scripts/import_products.sql`, not by `create_all` (no migrations yet). `embedding` is `Vector(1024)` and deferred.
- `app/api/products.py`: `GET /products/` (limit/offset) and `GET /products/{id}`.
- `app/api/auth.py` is OAuth2 password-flow + JWT auth (PyJWT, HS256; `pwdlib[argon2]` password hashing), adapted from the FastAPI tutorial. It defines `router = APIRouter()` with `POST /token`, `GET /users/me/`, `GET /users/me/items/`, plus the `get_current_user` / `get_current_active_user` dependencies for protecting routes. The router is included in `main.py` with no prefix; if you add one, update `OAuth2PasswordBearer(tokenUrl="token")` to match.

Things to know about the current state:

- Users come from an in-memory `fake_users_db` dict (not the database yet).
