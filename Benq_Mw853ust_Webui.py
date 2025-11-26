#!/usr/bin/env python3
"""Launcher for the split web UI package.

This file is intentionally small — it creates the Flask app from the
`webui` package and runs it. All routes, templates and static files live
inside the `webui` package.
"""
from webui import create_app

app = create_app()


if __name__ == '__main__':
  # print defaults for convenience
  try:
    from webui.commands import PROJECTOR_IP, PROJECTOR_PORT
    print('BenQ MW853UST Local Web UI starting...')
    print('Default projector IP:', PROJECTOR_IP, 'port', PROJECTOR_PORT)
  except Exception:
    pass
  app.run(host='0.0.0.0', port=5000, debug=True)
