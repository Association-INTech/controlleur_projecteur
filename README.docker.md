# Docker

Build the image from the repository root:

```bash
docker build -t controlleur_projecteur .
```

Run the container:

```bash
docker run --rm -p 5000:5000 controlleur_projecteur
```

Or with `docker-compose` (recommended for development):

```bash
docker-compose up --build
```

Notes:
- The app listens on port `5000` inside the container and is published to the same host port by default.
- The `docker-compose` setup mounts the project into the container so code changes are visible without rebuilding.
