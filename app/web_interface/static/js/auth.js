// web_interface/static/js/auth.js
// handle nav display and logout

function isLogged(){
  return !!localStorage.getItem('access_token');
}

function updateNav(){
  if (isLogged()){
    document.getElementById('nav-login').classList.add('hidden');
    document.getElementById('nav-register').classList.add('hidden');
    const out = document.getElementById('nav-logout');
    out.classList.remove('hidden');
    out.onclick = async ()=> {
      try {
        await httpPostJson('/api/public/auth/logout', {}); // cookie-based revoke on server
      } catch(e){ console.warn(e); }
      localStorage.removeItem('access_token');
      window.location.href = '/';
    };
  } else {
    document.getElementById('nav-login').classList.remove('hidden');
    document.getElementById('nav-register').classList.remove('hidden');
    document.getElementById('nav-logout').classList.add('hidden');
  }
}
document.addEventListener('DOMContentLoaded', updateNav);
