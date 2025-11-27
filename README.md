# controlleur_projecteur

BenQ MW853UST local Web UI — a small Flask app to control a projector on a local network.

## Quick overview

- Launcher: `Benq_Mw853ust_Webui.py` (creates the Flask `app` from the `webui` package)
- App entrypoint: `webui.create_app()` — routes, templates, and static files live in the `webui/` package

## Requirements

- Python 3.11+

## Run locally (recommended for Raspberry Pi or small devices)

1. Create and activate a virtual environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```



3.  Run directly with Python for quick debugging:

```bash
python Benq_Mw853ust_Webui.py
```

4. Run with Gunicorn for production use and final debuging:

```bash
# from project root with venv activated
./.venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 1 Benq_Mw853ust_Webui:app
```

## Systemd service (recommended on the Pi)

Create a service file (example provided as `benq-web.service` in the repo). Copy it to `/etc/systemd/system/` and then enable & start:

```bash
sudo cp benq-web.service /etc/systemd/system/benq-web.service
sudo systemctl daemon-reload
sudo systemctl enable --now benq-web.service
sudo journalctl -u benq-web -f
```

Edit the `benq-web.service` file to set the correct `User` and `WorkingDirectory` for your system.

## Makefile

Common conveniences are available via `make` (see `Makefile`):

```bash
make install           # create .venv and install requirements
make venv-recreate     # force recreate .venv and reinstall
make run               # run production server (gunicorn)
make run-debug         # run with python for quick debugging
make service-install   # install and enable systemd service (requires sudo)
make service-start     # start systemd service
make service-stop      # stop systemd service
make service-status    # check service status
make clean             # remove .venv
```

## Disclaimer

Ce projet est quasiment exclusivement vibe-coder.
