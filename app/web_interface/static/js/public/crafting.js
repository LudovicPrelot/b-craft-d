// web_interface/static/js/user/crafting.js
async function initCrafting(){
  try{
    const possible = await httpGetJson('/api/user/crafting/possible');
    const sel = document.getElementById('recipe-select');
    sel.innerHTML = (possible || []).map(r=>`<option value="${r.id||r.name}">${r.name||r.id}</option>`).join('');
    document.getElementById('craft-form').addEventListener('submit', async (e)=>{
      e.preventDefault();
      const rid = sel.value;
      try{
        const res = await httpPostJson('/api/user/crafting/craft', { recipe: rid });
        document.getElementById('craft-result').innerText = JSON.stringify(res);
      }catch(err){ document.getElementById('craft-result').innerText = 'Erreur: '+err.message; }
    });
  }catch(e){ console.error(e); document.getElementById('possible-recipes').innerText='Erreur'; }
}
