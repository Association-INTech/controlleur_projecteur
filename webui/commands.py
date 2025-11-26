import socket
import time

# Configuration - change projector_ip to your projector's IP or leave blank to configure in UI
PROJECTOR_IP = "192.168.1.5"
PROJECTOR_PORT = 8000
TCP_TIMEOUT = 2.0  # seconds to wait for response
SEND_LEADING_TRAILING_CR = False  # if True, will wrap commands with \r on both sides

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
