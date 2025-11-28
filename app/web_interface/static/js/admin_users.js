async function admin_headers(){ return {"Content-Type":"application/json","Authorization":"Bearer "+localStorage.getItem("access_token")} }

async function refreshUsers(){
  const res = await fetch('/admin/users', { headers: await admin_headers() });
  if(!res.ok){ alert('Erreur'); return; }
  const data = await res.json();
  const tbody = document.querySelector('#usersTable tbody');
  tbody.innerHTML = '';
  data.forEach(u=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.id}</td><td>${u.login}</td><td>${u.mail}</td><td>${u.xp||0}</td><td>${u.level||1}</td>
      <td>
        <button class="del" data-id="${u.id}">Suppr</button>
        <button class="grant" data-id="${u.id}">Grant XP 100</button>
      </td>`;
    tbody.appendChild(tr);
  });

  document.querySelectorAll('.del').forEach(b=> b.onclick = async ()=> {
    if(!confirm('Supprimer?')) return;
    const id = b.dataset.id;
    const r = await fetch('/admin/users/'+id, { method:'DELETE', headers: await admin_headers() });
    if(r.ok) refreshUsers(); else alert('Erreur');
  });

  document.querySelectorAll('.grant').forEach(b=> b.onclick = async ()=>{
    const id = b.dataset.id;
    const r = await fetch('/admin/users/'+id+'/grant_xp', { method:'POST', headers: await admin_headers(), body: JSON.stringify({amount:100})});
    if(r.ok) refreshUsers(); else alert('Erreur');
  });
}

document.getElementById('refresh').onclick = refreshUsers;

document.getElementById('createForm').onsubmit = async e=>{
  e.preventDefault();
  const f = new FormData(e.target);
  const body = {
    firstname: f.get('firstname'), lastname: f.get('lastname'),
    mail: f.get('mail'), login: f.get('login'), password: f.get('password'),
    profession: f.get('profession'), biome: f.get('biome')
  };
  const r = await fetch('/admin/users', { method:'POST', headers: await admin_headers(), body: JSON.stringify(body)});
  if(r.ok){ alert('created'); refreshUsers(); e.target.reset(); } else alert('Erreur');
};
