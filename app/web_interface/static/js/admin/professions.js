// ========================================
// JS – CRUD complet pour professions
// ========================================

const API_BASE = "/api/admin/professions";

// --------------------------------------------------------
// LIST
// --------------------------------------------------------
async function loadProfessions() {
    const res = await fetch(API_BASE + "/");
    const data = await res.json();

    const tbody = document.querySelector("#prof-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";

    data.forEach(prof => {
        tbody.innerHTML += `
            <tr>
                <td>${prof.id}</td>
                <td>${prof.name}</td>

                <td>
                    <a class="btn btn-sm btn-info" href="/admin/professions/${prof.id}">Voir</a>
                    <a class="btn btn-sm btn-warning" href="/admin/professions/${prof.id}/edit">Modifier</a>
                    <button class="btn btn-sm btn-danger"
                            onclick="deleteProfession('${prof.id}')">
                        Supprimer
                    </button>
                </td>
            </tr>
        `;
    });
}

// --------------------------------------------------------
// CREATE
// --------------------------------------------------------
async function createProfession(ev) {
    ev.preventDefault();

    const form = ev.target;
    const payload = {
        id: form.id.value,
        name: form.name.value
    };

    const res = await fetch(API_BASE + "/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        window.location.href = "/admin/professions";
    } else {
        alert("Erreur lors de la création.");
    }
}

// --------------------------------------------------------
// UPDATE
// --------------------------------------------------------
async function updateProfession(ev) {
    ev.preventDefault();

    const form = ev.target;
    const profId = form.dataset.id;

    const payload = {
        name: form.name.value
    };

    const res = await fetch(API_BASE + "/" + profId, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        window.location.href = "/admin/professions";
    } else {
        alert("Erreur lors de la mise à jour.");
    }
}

// --------------------------------------------------------
// DELETE
// --------------------------------------------------------
async function deleteProfession(id) {
    if (!confirm("Supprimer " + id + " ?")) return;

    const res = await fetch(API_BASE + "/" + id, {
        method: "DELETE"
    });

    if (res.ok) {
        window.location.reload();
    } else {
        alert("Erreur lors de la suppression.");
    }
}

// --------------------------------------------------------
// Chargement automatique si table présente
// --------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    if (document.querySelector("#prof-table-body")) loadProfessions();

    const formCreate = document.querySelector("#form-create");
    if (formCreate) formCreate.addEventListener("submit", createProfession);

    const formEdit = document.querySelector("#form-edit");
    if (formEdit) formEdit.addEventListener("submit", updateProfession);
});
