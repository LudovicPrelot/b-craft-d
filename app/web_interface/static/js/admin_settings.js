async function adminHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("access_token")
    };
}

async function loadSettings() {
    const res = await fetch("/admin/settings", { headers: await adminHeaders() });
    const settings = await res.json();

    document.querySelector("input[name='enable_loot']").checked = settings.enable_loot;
    document.querySelector("input[name='enable_stats']").checked = settings.enable_stats;
    document.querySelector("input[name='enable_quests']").checked = settings.enable_quests;
}

document.getElementById("settingsForm").onsubmit = async (e) => {
    e.preventDefault();

    const settings = {
        enable_loot: document.querySelector("input[name='enable_loot']").checked,
        enable_stats: document.querySelector("input[name='enable_stats']").checked,
        enable_quests: document.querySelector("input[name='enable_quests']").checked
    };

    const res = await fetch("/admin/settings", {
        method: "POST",
        headers: await adminHeaders(),
        body: JSON.stringify(settings)
    });

    if (res.ok) {
        alert("Paramètres sauvegardés !");
    } else {
        alert("Erreur lors de la sauvegarde.");
    }
};

loadSettings();
