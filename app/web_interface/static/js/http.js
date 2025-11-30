// web_interface/static/js/http.js
// Simple fetch wrapper & auth helpers

function authHeaders() {
  const t = localStorage.getItem('access_token');
  const h = { 'Content-Type': 'application/json' };
  if (t) h['Authorization'] = 'Bearer ' + t;
  return h;
}

async function httpGetJson(path) {
  const r = await fetch(path, { headers: authHeaders() });
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(txt || 'HTTP error '+r.status);
  }
  return r.json();
}

async function httpPostJson(path, body) {
  const r = await fetch(path, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body || {})
  });
  if (!r.ok) {
    const json = await r.json().catch(()=>null);
    throw new Error((json && (json.detail||json.error)) || ('HTTP '+r.status));
  }
  return r.json();
}

async function httpDeleteJson(path) {
  const r = await fetch(path, { method: 'DELETE', headers: authHeaders() });
  if (!r.ok) {
    const json = await r.json().catch(()=>null);
    throw new Error((json && (json.detail||json.error)) || ('HTTP '+r.status));
  }
  return r.json();
}
