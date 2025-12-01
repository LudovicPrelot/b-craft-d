document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("professions-list");

    const data = await httpGetJson("/api/moderator/professions");

    container.innerHTML = Object.entries(data.professions).map(([key, p]) =>
        `<div class="profession-item">${p.name}</div>`)
        .join("");
});
