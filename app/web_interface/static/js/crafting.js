async function loadInventory() {
    const inv = await apiGet("/inventory/");
    document.getElementById("invDisplay").textContent = JSON.stringify(inv, null, 2);
}

async function loadPossible() {
    const list = await apiGet("/crafting/possible");
    const ul = document.getElementById("recipesList");
    ul.innerHTML = "";

    list.forEach(rec => {
        const li = document.createElement("li");
        li.innerHTML = `
            <strong>${rec.id}</strong> → ${rec.output}
            <pre>${JSON.stringify(rec.ingredients)}</pre>
            <button data-id="${rec.id}" class="craftBtn">Craft</button>
        `;
        ul.appendChild(li);
    });

    document.querySelectorAll(".craftBtn").forEach(btn => {
        btn.onclick = async () => {
            const id = btn.dataset.id;
            const r = await apiPost("/crafting/craft", { recipe_id: id });
            alert("Craft réussi: " + r.produced.output);
            loadInventory();
            loadPossible();
        };
    });
}

document.getElementById("refreshRecipes").onclick = loadPossible;
loadInventory();
loadPossible();
