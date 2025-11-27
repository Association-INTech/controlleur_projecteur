FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal system deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata so we can leverage caching for installs
COPY pyproject.toml /app/

# Install runtime dependencies using `uv` (reads `pyproject.toml`) and ensure
# `gunicorn` is available for production serving.
RUN pip install --no-cache-dir uv \
    && uv sync

# Ensure `uv`'s created virtualenv (commonly `.venv`) is on PATH so installed
# packages (Flask, gunicorn) are discoverable by the runtime `gunicorn` binary.
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application source
COPY . /app

EXPOSE 5000

# Run the Flask app via gunicorn exposing the `app` in the launcher module
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "Benq_Mw853ust_Webui:app"]
