// web_interface/static/js/public/recipes.js
async function loadRecipes(){
  try{
    const data = await httpGetJson('/api/public/recipes');
    const el = document.getElementById('recipes-list');
    if (!data || !data.length) { el.innerText = 'Aucune recette'; return; }
    el.innerHTML = '<ul class="space-y-2">'+data.map(r=>`<li class="p-2 border rounded"><strong>${r.name||r.id}</strong><div class="text-sm">${r.description||''}</div></li>`).join('')+'</ul>';
  }catch(e){ console.error(e); document.getElementById('recipes-list').innerText='Erreur'; }
}
