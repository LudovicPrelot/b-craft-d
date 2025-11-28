async function adminHeaders(){
    return {
        "Authorization": "Bearer " + localStorage.getItem("access_token")
    };
}

async function loadFeatureStatus() {
    const res = await fetch("/admin/settings", { headers: await adminHeaders() });
    const s = await res.json();

    const div = document.getElementById("featureStatus");
    div.innerHTML = `
        <ul>
            <li>Loot: <b>${s.enable_loot ? "Activé" : "Désactivé"}</b></li>
            <li>Stats: <b>${s.enable_stats ? "Activé" : "Désactivé"}</b></li>
            <li>Quêtes: <b>${s.enable_quests ? "Activé" : "Désactivé"}</b></li>
        </ul>
    `;
}

loadFeatureStatus();
