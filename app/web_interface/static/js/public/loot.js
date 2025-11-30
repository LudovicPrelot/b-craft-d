// web_interface/static/js/user/loot.js
async function initLoot(){
  const form = document.getElementById('loot-form');
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const env = form.environment.value || 'default';
    try{
      const res = await httpPostJson('/api/user/loot/collect?attempts=1&season=summer&weather=sunny&event=', { });
      document.getElementById('loot-results').innerText = JSON.stringify(res);
    }catch(err){ document.getElementById('loot-results').innerText = 'Erreur: '+err.message; }
  });
}
