from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app
import os
from .commands import COMMAND_MAP, send_projector_command, PROJECTOR_IP, PROJECTOR_PORT

bp = Blueprint('webui', __name__, template_folder='templates', static_folder='static')


@bp.route('/')
def index():
    return render_template('index.html', default_ip=PROJECTOR_IP, default_port=PROJECTOR_PORT)


@bp.route('/api/preset', methods=['POST'])
def api_preset():
    req = request.get_json(force=True)
    key = req.get('key')
    cfg = req.get('cfg') or {}
    ip = cfg.get('ip') or PROJECTOR_IP
    port = int(cfg.get('port') or PROJECTOR_PORT)
    wrap = bool(cfg.get('wrapcr'))

    cmd = COMMAND_MAP.get(key)
    if not cmd:
        current_app.logger.info('api_preset: unknown key %s', key)
        return jsonify({'error': 'unknown preset key'}), 400
    current_app.logger.info('api_preset: sending %s to %s:%s (wrap=%s)', key, ip, port, wrap)
    resp = send_projector_command(ip, port, cmd, wrap_cr=wrap)
    current_app.logger.info('api_preset: response length %d', len(resp) if isinstance(resp, str) else 0)
    return jsonify({'sent': cmd, 'response': resp})


@bp.route('/api/raw', methods=['POST'])
def api_raw():
    req = request.get_json(force=True)
    cmd = req.get('cmd')
    cfg = req.get('cfg') or {}
    ip = cfg.get('ip') or PROJECTOR_IP
    port = int(cfg.get('port') or PROJECTOR_PORT)
    wrap = bool(cfg.get('wrapcr'))

    if not cmd:
        current_app.logger.info('api_raw: no command provided')
        return jsonify({'error': 'no command provided'}), 400

    # If user inputs with angle-bracketed <CR>, replace with actual CR marker for convenience
    if '<CR>' in cmd:
        cmd = cmd.replace('<CR>', '')

    current_app.logger.info('api_raw: sending raw cmd to %s:%s (wrap=%s)', ip, port, wrap)
    resp = send_projector_command(ip, port, cmd, wrap_cr=wrap)
    current_app.logger.info('api_raw: response length %d', len(resp) if isinstance(resp, str) else 0)
    return jsonify({'sent': cmd, 'response': resp})


@bp.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify({'ok': True})


@bp.route('/favicon.ico')
def favicon():
    # No favicon provided — return 204 No Content to avoid 404 noise
    return ('', 204)


@bp.route('/manual.pdf')
def manual_pdf():
    """Serve the RS232 control PDF located next to this package."""
    filename = "RS232 Control Guide_0_Windows7_Windows8_WinXP.pdf"
    dirpath = os.path.dirname(os.path.dirname(__file__))
    full = os.path.join(dirpath, filename)
    if not os.path.exists(full):
        current_app.logger.info('manual_pdf: file not found %s', full)
        return jsonify({'error': 'manual not found on server'}), 404
    return send_from_directory(dirpath, filename, as_attachment=True)
