// static/js/public/resources.js

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("resources-container");

    try {
        const response = await fetch("/api/public/resources/");
        const data = await response.json();

        container.innerHTML = "";

        Object.entries(data).map(([key, resource]) => {
            const div = document.createElement("div");
            div.className = "resource-card";
            div.innerHTML = `
                <h3>${resource.name || key}</h3>
                <p><strong>ID:</strong> ${key}</p>
                <p><strong>Rareté:</strong> ${resource.rarity || "?"}</p>
            `;
            container.appendChild(div);
        });

    } catch (err) {
        container.innerHTML = "<p class='error'>Impossible de charger les ressources.</p>";
        console.error(err);
    }
});
