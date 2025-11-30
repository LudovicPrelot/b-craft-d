// web_interface/static/js/public/resources.js
async function loadResources(){
  try{
    const data = await httpGetJson('/api/public/resources/');
    const el = document.getElementById('resources-list');
    if (!data || !data.length) { el.innerText = 'Aucune ressource'; return; }
    el.innerHTML = '<ul class="space-y-2">'+data.map(r=>`<li class="p-2 border rounded">${r.name||r.id} — <small>${r.type||''}</small></li>`).join('')+'</ul>';
  }catch(e){ console.error(e); document.getElementById('resources-list').innerText='Erreur'; }
}
