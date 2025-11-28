async function admin_headers(){ return {"Content-Type":"application/json","Authorization":"Bearer "+localStorage.getItem("access_token")} }

document.getElementById('getUser').onclick = async ()=>{
  const id = document.getElementById('userId').value;
  const r = await fetch('/admin/users/'+id, { headers: await admin_headers() });
  if(!r.ok){ alert('User not found'); return; }
  const j = await r.json();
  document.getElementById('userOut').textContent = JSON.stringify(j, null, 2);
};

document.getElementById('grantForm').onsubmit = async e=>{
  e.preventDefault();
  const id = document.getElementById('userId').value;
  const f = new FormData(e.target);
  const amount = parseInt(f.get('amount'), 10);
  const r = await fetch('/admin/users/'+id+'/grant_xp', { method:'POST', headers: await admin_headers(), body: JSON.stringify({amount: amount}) });
  if(r.ok){ alert('XP accordée'); document.getElementById('getUser').click(); } else alert('Erreur');
};
