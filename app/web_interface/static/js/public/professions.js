// static/js/public/professions.js

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("professions-container");

    try {
        const response = await fetch("/api/public/professions");
        const data = await response.json();

        container.innerHTML = "";

        Object.entries(data).map(([key, profession]) => {
            const div = document.createElement("div");
            div.className = "profession-card";
            div.innerHTML = `
                <h3>${profession.name || key}</h3>
                <p><strong>ID:</strong> ${key}</p>
                <p><strong>Classes secondaires:</strong></p>
                <ul>
                    ${Object.entries(profession.subclasses || {})
                        .map(([k, name]) => `<li>${name}</li>`)
                        .join("")}
                </ul>
            `;
            container.appendChild(div);
        });

    } catch (err) {
        container.innerHTML = "<p class='error'>Impossible de charger les professions.</p>";
        console.error(err);
    }
});