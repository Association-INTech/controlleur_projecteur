#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "flask",
# ]
# ///
"""
BenQ MW853UST local Web UI (Flask)

Single-file app that serves a small web interface and an API to send RS232-over-TCP
commands to the projector (port 8000). Designed to run locally now and on a Raspberry Pi later.

Usage:
  pip install flask
  python3 benq_web_ui.py

Open http://localhost:5000 in your browser.

Notes:
- The projector expects commands like: *pow=on#  (optionally wrapped in CR \r before/after)
- This script sends the command and reads the projector's immediate response, then returns it to the UI.
- The uploaded image (manual screenshot) is referenced below; if you want it served from static files,
  move it into a static/ folder or let the environment transform the local path.

Uploaded image path (for your environment to convert):
/mnt/data/fc693af6-c529-46d0-9e08-1dff2300ad99.png
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
import socket
import threading
import time

# Configuration - change projector_ip to your projector's IP or leave blank to configure in UI
PROJECTOR_IP = "192.168.1.5"  # default, update as needed
PROJECTOR_PORT = 8000
TCP_TIMEOUT = 2.0  # seconds to wait for response
SEND_LEADING_TRAILING_CR = False  # if True, will wrap commands with \r on both sides

app = Flask(__name__)

# Mapping of friendly actions to actual command strings (without <CR>)
COMMAND_MAP = {
    # Power
    "pow_on": "*pow=on#",
    "pow_off": "*pow=off#",
    "pow_status": "*pow=?#",
    # Sources (a subset - add more as needed)
    "sour_rgb": "*sour=RGB#",
    "sour_hdmi": "*sour=hdmi#",
    "sour_dvid": "*sour=dvid#",
    "sour_vid": "*sour=vid#",
    "sour_hdbaset": "*sour=hdbaset#",
    "sour_dp": "*sour=dp#",
    # Common navigation
    "menu_on": "*menu=on#",
    "menu_off": "*menu=off#",
    "menu_status": "*menu=?#",
    "enter": "*enter#",
    "up": "*up#",
    "down": "*down#",
    "left": "*left#",
    "right": "*right#"
}

# Helper: send a single command and return projector response (string)
def send_projector_command(host: str, port: int, cmd: str, timeout: float = TCP_TIMEOUT, wrap_cr: bool = SEND_LEADING_TRAILING_CR) -> str:
    """Open TCP socket, send command, read available response, and close."""
    # ensure command ends with '#' as per protocol
    if not cmd.endswith('#'):
        cmd = cmd + '#'
    # optionally wrap with carriage return
    if wrap_cr:
        raw = ('\r' + cmd + '\r').encode('ascii')
    else:
        raw = cmd.encode('ascii')

    data = b''
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            s.sendall(raw)
            # read until timeout
            start = time.time()
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                except socket.timeout:
                    break
                # safety TTL
                if time.time() - start > (timeout + 1):
                    break
    except Exception as e:
        return f"ERROR: {e}"

    try:
        return data.decode('ascii', errors='replace') if data else ''
    except Exception:
        return repr(data)


# Basic index page with a few controls
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>BenQ MW853UST - Local Control</title>
  <style>
    body { font-family: system-ui, -apple-system, Arial, sans-serif; margin: 20px; }
    .row { display:flex; gap:8px; margin-bottom:8px; }
    button { padding:8px 12px; }
    select { padding:6px; }
    /* log height will be flexible to fill the right column */
    #log { white-space: pre-wrap; background:#f7f7f7; padding:10px; border:1px solid #ddd; overflow:auto; }
    .panel { border:1px solid #ddd; padding:12px; margin-bottom:12px; border-radius:6px; }
    img.manual { max-width:100%; height:auto; border:1px solid #ccc; }
  </style>
</head>
<body>
  <h2>BenQ MW853UST - Local Web UI</h2>




    <style>
      /* Two-column layout: controls (left) and log (right). Make the container fill remaining viewport height so the right column can stretch. */
      .container { display:flex; gap:16px; align-items:stretch; min-height: calc(100vh - 120px); }
      .left { flex: 1 1 60%; }
      .right { flex: 0 0 380px; }
      .right .panel { height:100%; display:flex; flex-direction:column; }
      #log { flex:1 1 auto; overflow:auto; }
      /* navigation pad (arrow keys) styling */
      .nav-pad { display:grid; grid-template-columns: 56px 56px 56px; gap:6px; justify-content:center; align-items:center; margin-top:8px; }
      .nav-pad button { width:56px; height:40px; }
      @media (max-width: 900px) { .container { flex-direction:column; min-height: auto; } .right { flex: 1 1 auto; max-width: 100%; } }
    </style>

    <div class="container">
      <div class="left">
        <div class="panel">
          <label>Projector IP: <input id="ip" value="{{ default_ip }}"></label>
          <label>Port: <input id="port" value="{{ default_port }}" style="width:70px"></label>
          <label><input type="checkbox" id="wrapcr"> Wrap with CR</label>
          <button id="savecfg">Save</button>
        </div>

        <div class="panel">
          <h3>Documentation</h3>
          <div class="row">
            <a href="/manual.pdf"><button>Download RS232 Control Guide (PDF)</button></a>
          </div>
        </div>

        <div class="panel">
          <div class="row">
            <input id="rawcmd" placeholder="Type raw command like *pow=?#" style="flex:1"> <button onclick="sendRaw()">Send Raw</button>
          </div>
          <h3>Power</h3>
          <div class="row">
            <button onclick="sendPreset('pow_on')">Power On</button>
            <button onclick="sendPreset('pow_off')">Power Off</button>
            <!--- <button onclick="sendPreset('pow_status')">Power Status</button> -->
          </div>

          <h3>Source</h3>
          <div class="row">
            <button onclick="sendPreset('sour_rgb')">Computer (VGA)</button>
            <button onclick="sendPreset('sour_hdmi')">HDMI</button>
            <button onclick="sendPreset('sour_dvid')">DVI</button>
            <button onclick="sendPreset('sour_vid')">Composite</button>
          </div>

          <h3>Menu / Navigation</h3>
              <div class="row">
                  <button onclick="sendPreset('menu_on')">Menu On</button>
                  <button onclick="sendPreset('menu_off')">Menu Off</button>
                  <div><button onclick="sendPreset('enter')">Enter</button></div>
                  
              </div>

              <!-- Arrow-key style navigation grid -->
              <div class="nav-pad" role="group" aria-label="navigation pad">
                <div></div>
                <div><button onclick="sendPreset('up')">Up</button></div>
                <div></div>

                <div><button onclick="sendPreset('left')">Left</button></div>
                <div><button onclick="sendPreset('down')">Down</button></div>
                <div><button onclick="sendPreset('right')">Right</button></div>
              </div>
        </div>
      </div>

      <div class="right">
        <div class="panel">
          <h3>Response Log</h3>
          <div id="log"></div>
        </div>
      </div>
    </div>
    

  </div>

  <!-- Manual screenshot panel removed -->

<script>
function appendLog(text){
  const el = document.getElementById('log');
  const now = new Date().toLocaleTimeString();
  el.textContent = now + ' — ' + text + String.fromCharCode(10) + el.textContent;
}

function getCfg(){
  return { ip: document.getElementById('ip').value, port: parseInt(document.getElementById('port').value || '{{ default_port }}', 10), wrapcr: document.getElementById('wrapcr').checked };
}

function saveCfg(){
  localStorage.setItem('benq_cfg', JSON.stringify(getCfg()));
  appendLog('Saved configuration');
}

document.getElementById('savecfg').addEventListener('click', saveCfg);

window.addEventListener('load', ()=>{
  const raw = localStorage.getItem('benq_cfg');
  if(raw){
    try{ const o=JSON.parse(raw); document.getElementById('ip').value=o.ip; document.getElementById('port').value=o.port; document.getElementById('wrapcr').checked=o.wrapcr; }catch(e){}
  }
});

async function sendPreset(key){
  const cfg = getCfg();
  appendLog('Sending ' + key + '...');
  try {
    const res = await fetch('/api/preset', {method:'POST', body: JSON.stringify({key, cfg}), headers: {'Content-Type':'application/json'}});
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      const txt = await res.text();
      appendLog('HTTP ' + res.status + ' ' + res.statusText + String.fromCharCode(10) + txt);
      return;
    }
    const j = await res.json();
    appendLog('> ' + (j.sent || '') + String.fromCharCode(10) + '< ' + (j.response || j.error || 'no response'));
  } catch (err) {
    appendLog('Fetch error: ' + err);
  }
}

async function sendRaw(){
  const cmd = document.getElementById('rawcmd').value;
  if(!cmd) return;
  const cfg = getCfg();
  appendLog('Sending raw: ' + cmd);
  try {
    const res = await fetch('/api/raw', {method:'POST', body: JSON.stringify({cmd, cfg}), headers: {'Content-Type':'application/json'}});
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      const txt = await res.text();
      appendLog('HTTP ' + res.status + ' ' + res.statusText + String.fromCharCode(10) + txt);
      return;
    }
    const j = await res.json();
    appendLog('> ' + (j.sent || '') + String.fromCharCode(10) + '< ' + (j.response || j.error || 'no response'));
  } catch (err) {
    appendLog('Fetch error: ' + err);
  }
}

// Expose functions to global scope for inline `onclick` handlers
window.sendPreset = sendPreset;
window.sendRaw = sendRaw;

// Keyboard support: capture arrow keys and Enter to navigate the menu
window.addEventListener('keydown', function(e){
  // Ignore when typing in inputs or editable elements
  const active = document.activeElement;
  if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) return;

  // Debug: surface key presses to the on-page log and console for easier troubleshooting
  try{ appendLog('Keydown: ' + e.key); }catch(_){ /* noop if log not present */ }
  console.debug && console.debug('BenQ: keydown', e.key, 'active=', active && active.tagName);

  const key = e.key;
  switch(key){
    case 'ArrowUp':
    case 'Up':
      e.preventDefault(); sendPreset('up'); break;
    case 'ArrowDown':
    case 'Down':
      e.preventDefault(); sendPreset('down'); break;
    case 'ArrowLeft':
    case 'Left':
      e.preventDefault(); sendPreset('left'); break;
    case 'ArrowRight':
    case 'Right':
      e.preventDefault(); sendPreset('right'); break;
    case 'Enter':
      e.preventDefault(); sendPreset('enter'); break;
    default:
      break;
  }
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, default_ip=PROJECTOR_IP, default_port=PROJECTOR_PORT)
@app.route('/api/preset', methods=['POST'])
def api_preset():
    req = request.get_json(force=True)
    key = req.get('key')
    cfg = req.get('cfg') or {}
    ip = cfg.get('ip') or PROJECTOR_IP
    port = int(cfg.get('port') or PROJECTOR_PORT)
    wrap = bool(cfg.get('wrapcr'))

    cmd = COMMAND_MAP.get(key)
    if not cmd:
        app.logger.info('api_preset: unknown key %s', key)
        return jsonify({'error': 'unknown preset key'}), 400

    app.logger.info('api_preset: sending %s to %s:%s (wrap=%s)', key, ip, port, wrap)
    resp = send_projector_command(ip, port, cmd, wrap_cr=wrap)
    app.logger.info('api_preset: response length %d', len(resp) if isinstance(resp, str) else 0)
    return jsonify({'sent': cmd, 'response': resp})


@app.route('/api/raw', methods=['POST'])
def api_raw():
    req = request.get_json(force=True)
    cmd = req.get('cmd')
    cfg = req.get('cfg') or {}
    ip = cfg.get('ip') or PROJECTOR_IP
    port = int(cfg.get('port') or PROJECTOR_PORT)
    wrap = bool(cfg.get('wrapcr'))

    if not cmd:
        app.logger.info('api_raw: no command provided')
        return jsonify({'error': 'no command provided'}), 400

    # If user inputs with angle-bracketed <CR>, replace with actual CR marker for convenience
    if '<CR>' in cmd:
        cmd = cmd.replace('<CR>', '')

    app.logger.info('api_raw: sending raw cmd to %s:%s (wrap=%s)', ip, port, wrap)
    resp = send_projector_command(ip, port, cmd, wrap_cr=wrap)
    app.logger.info('api_raw: response length %d', len(resp) if isinstance(resp, str) else 0)
    return jsonify({'sent': cmd, 'response': resp})


@app.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify({'ok': True})


@app.route('/favicon.ico')
def favicon():
  # No favicon provided — return 204 No Content to avoid 404 noise
  return ('', 204)


@app.route('/manual.pdf')
def manual_pdf():
  """Serve the RS232 control PDF located next to this script."""
  filename = "RS232 Control Guide_0_Windows7_Windows8_WinXP.pdf"
  dirpath = os.path.dirname(__file__)
  full = os.path.join(dirpath, filename)
  if not os.path.exists(full):
    app.logger.info('manual_pdf: file not found %s', full)
    return jsonify({'error': 'manual not found on server'}), 404
  return send_from_directory(dirpath, filename, as_attachment=True)


if __name__ == '__main__':
    print('BenQ MW853UST Local Web UI starting...')
    print('Default projector IP:', PROJECTOR_IP, 'port', PROJECTOR_PORT)
    app.run(host='0.0.0.0', port=5000, debug=True)
