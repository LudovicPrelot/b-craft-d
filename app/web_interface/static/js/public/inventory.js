// web_interface/static/js/user/inventory.js
async function initInventory(){
  await refreshInventory();
  document.getElementById('add-item-form').addEventListener('submit', async (e)=>{
    e.preventDefault();
    const f = e.target;
    try {
      await httpPostJson('/api/user/inventory/add?item='+encodeURIComponent(f.item.value)+'&qty='+encodeURIComponent(f.qty.value||1), {});
      await refreshInventory();
    } catch (err) {
      alert('Erreur: '+err.message);
    }
  });
}

async function refreshInventory(){
  try{
    const res = await httpGetJson('/api/user/inventory/');
    const inv = res.inventory || {};
    const el = document.getElementById('inventory-table');
    el.innerHTML = '<table class="w-full"><thead><tr><th>Item</th><th>Qty</th><th>Actions</th></tr></thead><tbody>' +
      Object.entries(inv).map(([k,v])=>`<tr class="border-t"><td>${k}</td><td>${v}</td><td><button class="btn" onclick="removeItem('${k}')">-</button></td></tr>`).join('') +
      '</tbody></table>';
  }catch(e){ console.error(e); document.getElementById('inventory-table').innerText='Erreur'; }
}

async function removeItem(item){
  try{
    await httpPostJson('/api/user/inventory/remove?item='+encodeURIComponent(item)+'&qty=1', {});
    await refreshInventory();
  }catch(e){ alert('Erreur'); }
}
