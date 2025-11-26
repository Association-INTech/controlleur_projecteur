// read server-provided defaults from the JSON script block (id="DEFAULTS")
(function(){
  try{
    const def = document.getElementById('DEFAULTS');
    if(def && def.textContent){
      window.DEFAULTS = JSON.parse(def.textContent);
    }
  }catch(e){
    window.DEFAULTS = window.DEFAULTS || { ip: '127.0.0.1', port: 8000 };
  }
})();

function appendLog(text){
  const el = document.getElementById('log');
  const now = new Date().toLocaleTimeString();
  el.textContent = now + ' — ' + text + String.fromCharCode(10) + el.textContent;
}

function getCfg(){
  return { ip: document.getElementById('ip').value, port: parseInt(document.getElementById('port').value || window.DEFAULTS.port, 10), wrapcr: document.getElementById('wrapcr').checked };
}

function saveCfg(){
  localStorage.setItem('benq_cfg', JSON.stringify(getCfg()));
  appendLog('Saved configuration');
}

document.getElementById('savecfg').addEventListener('click', saveCfg);

window.addEventListener('load', ()=>{
  // apply saved config or server defaults
  const raw = localStorage.getItem('benq_cfg');
  if(raw){
    try{ const o=JSON.parse(raw); document.getElementById('ip').value=o.ip; document.getElementById('port').value=o.port; document.getElementById('wrapcr').checked=o.wrapcr; }catch(e){}
  } else {
    // use server-provided defaults
    try{ document.getElementById('ip').value = window.DEFAULTS.ip; document.getElementById('port').value = window.DEFAULTS.port; }catch(e){}
  }

  // wire raw send button
  const rawBtn = document.getElementById('rawsend');
  if(rawBtn) rawBtn.addEventListener('click', sendRaw);
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

// expose sendPreset globally for inline handlers
window.sendPreset = sendPreset;
// also expose sendRaw for convenience
window.sendRaw = sendRaw;

// keyboard handler
window.addEventListener('keydown', function(e){
  const active = document.activeElement;
  if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) return;
  try{ appendLog('Keydown: ' + e.key); }catch(_){ }
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