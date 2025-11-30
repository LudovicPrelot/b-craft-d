// web_interface/static/js/public/professions.js
async function loadProfessions(){
  try{
    const data = await httpGetJson('/api/public/professions');
    const el = document.getElementById('prof-list');
    if (!data || !data.length) { el.innerText = 'Aucune profession'; return; }
    el.innerHTML = '<ul class="space-y-2">'+data.map(p=>`<li class="p-2 border rounded"><strong>${p.name||p.id}</strong> — ${p.description||''}</li>`).join('')+'</ul>';
  }catch(e){ console.error(e); document.getElementById('prof-list').innerText='Erreur'; }
}
