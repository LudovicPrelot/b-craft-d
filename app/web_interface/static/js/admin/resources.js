// web_interface/static/js/admin/resources.js
async function initAdminResources(){
  try{
    const r = await httpGetJson('/api/admin/resources/');
    document.getElementById('admin-resources').innerText = JSON.stringify(r, null, 2);
  }catch(e){ document.getElementById('admin-resources').innerText='Erreur'; }
}
