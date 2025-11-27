# controlleur_projecteur

BenQ MW853UST local Web UI — small Flask app to control a projector on a local network.

## Quick overview

- Launcher: `Benq_Mw853ust_Webui.py` (creates the Flask `app` from the `webui` package).
- App entrypoint: `webui.create_app()` — routes, templates, and static files live in the `webui/` package.

## Requirements

- Python 3.11+ (for local development)
- Docker & Docker Compose (optional, recommended for reproducible runs)

## Run locally (without Docker)

- Create a virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```


- Install dependencies (recommended with `uv`):

```bash
# sync dependencies declared in `pyproject.toml`
uv sync
```

- Run the app (recommended via `uv`):

```bash
uv run Benq_Mw853ust_Webui.py
# fallback: `python Benq_Mw853ust_Webui.py`
```

The app listens on `http://0.0.0.0:5000/` by default.

## Docker (recommended)

Build the image:

```bash
docker build -t controlleur_projecteur .
```

Run the container:

```bash
docker run --rm -p 5000:5000 controlleur_projecteur
```

Use docker-compose for development (live code mounts):

```bash
docker-compose up --build
```

## Makefile

Common conveniences are available via `make`:

```bash
make build       # build image
make run         # run image
make run-dev     # run with source mounted
make compose-up  # docker-compose up --build
make logs        # follow logs
make clean       # remove container/image
```

## Disclaimer

Ce projet est quasiment exclusivment vibe-coder.
