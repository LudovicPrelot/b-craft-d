// web_interface/static/js/admin/users.js
async function initAdminUsers(){
  await loadUsers();
  document.getElementById('reload-users').addEventListener('click', loadUsers);
  document.getElementById('create-user').addEventListener('click', async ()=>{
    const login = prompt('Login?'); if(!login) return;
    const payload = { login, password: 'changeme' };
    try { await httpPostJson('/api/admin/users/create', payload); await loadUsers(); } catch(e){ alert('Erreur'); }
  });
}

async function loadUsers(){
  try{
    const users = await httpGetJson('/api/admin/users/');
    const el = document.getElementById('users-table');
    el.innerHTML = '<table class="w-full"><thead><tr><th>Id</th><th>Login</th><th>Actions</th></tr></thead><tbody>' +
      users.map(u=>`<tr class="border-t"><td>${u.id}</td><td>${u.login}</td><td><button class="btn" onclick="deleteUser('${u.id}')">Suppr</button></td></tr>`).join('') +
      '</tbody></table>';
  }catch(e){ console.error(e); document.getElementById('users-table').innerText='Erreur'; }
}

async function deleteUser(uid){
  if(!confirm('Supprimer?')) return;
  await httpDeleteJson('/api/admin/users/'+encodeURIComponent(uid));
  await loadUsers();
}
