// static/js/public/recipes.js

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("recipes-container");

    try {
        const response = await fetch("/api/public/recipes");
        const data = await response.json();

        container.innerHTML = "";

        Object.entries(data).map(([key, recipe]) => {
            const div = document.createElement("div");
            div.className = "recipe-card";
            div.innerHTML = `
                <h3>${recipe.name || key}</h3>
                <p><strong>ID:</strong> ${key}</p>
                <p><strong>Ingrédients:</strong></p>
                <ul>
                    ${Object.entries(recipe.ingredients || {})
                        .map(([res, qty]) => `<li>${qty} × ${res}</li>`)
                        .join("")}
                </ul>
            `;
            container.appendChild(div);
        });

    } catch (err) {
        container.innerHTML = "<p class='error'>Impossible de charger les recettes.</p>";
        console.error(err);
    }
});
