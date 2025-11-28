async function admin_headers(){ return {"Content-Type":"application/json","Authorization":"Bearer "+localStorage.getItem("access_token")} }

document.getElementById('refresh').onclick = async ()=>{
  const r = await fetch('/admin/loot/tables', { headers: await admin_headers() });
  const j = await r.json();
  document.getElementById('lootOut').textContent = JSON.stringify(j, null, 2);
};

document.getElementById('lootForm').onsubmit = async e=>{
  e.preventDefault();
  const f = new FormData(e.target);
  const key = f.get('key');
  let payload;
  try{ payload = JSON.parse(f.get('payload')); } catch(err){ alert('Payload JSON invalide'); return; }
  const r = await fetch('/admin/loot/tables', { method:'POST', headers: await admin_headers(), body: JSON.stringify(Object.assign({key:key}, payload)) });
  if(r.ok){ alert('saved'); document.getElementById('refresh').click(); } else alert('Erreur');
};
