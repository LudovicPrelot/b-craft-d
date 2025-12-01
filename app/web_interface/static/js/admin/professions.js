async function loadProfessions() {
    const container = document.getElementById("professions-list");

    const data = await httpGetJson("/api/admin/professions");

    container.innerHTML = Object.entries(data.professions).map(([key, p]) =>
        `<div class="profession-item">
            <h3>${p.name}</h3>
            <p>${p.description || ""}</p>
            <button onclick="editProfession('${p.id}')">Modifier</button>
            <button onclick="deleteProfession('${p.id}')">Supprimer</button>
        </div>
    `).join("");
}

async function deleteProfession(id) {
    await httpDeleteJson(`/api/admin/professions/${id}`);
    loadProfessions();
}

function editProfession(id) {
    const form = document.getElementById("profession-form");
    form.innerHTML = `
        <h3>Modifier ${id}</h3>
        <input id="prof-name" placeholder="Nom">
        <textarea id="prof-desc" placeholder="Description"></textarea>
        <button onclick="saveProfession('${id}')">Enregistrer</button>
    `;
}

async function saveProfession(id) {
    const name = document.getElementById("prof-name").value;
    const desc = document.getElementById("prof-desc").value;

    await httpPutJson(`/api/admin/professions/${id}`, {
        name,
        description: desc,
    });

    loadProfessions();
}

document.addEventListener("DOMContentLoaded", loadProfessions);
