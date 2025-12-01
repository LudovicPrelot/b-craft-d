document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("professions-list");

    const data = await httpGetJson("/api/user/professions");

    container.innerHTML = Object.entries(data.professions).map(([key, p]) =>
        `<div class="profession-item">
            <h3>${p.name}</h3>
            <p>${p.description || ""}</p>
        </div>
    `).join("");
});
