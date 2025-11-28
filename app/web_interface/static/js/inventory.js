async function loadInventory() {
    const inv = await apiGet("/inventory/");
    const body = document.getElementById("invBody");
    body.innerHTML = "";

    Object.keys(inv).forEach(key => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${key}</td>
            <td>${inv[key]}</td>
            <td>
                <button class="remove1" data-item="${key}">-1</button>
                <button class="removeAll" data-item="${key}">Suppr</button>
            </td>`;
        body.appendChild(tr);
    });

    document.querySelectorAll(".remove1").forEach(btn => {
        btn.onclick = async () => {
            await apiPost(`/inventory/remove?item=${btn.dataset.item}&qty=1`);
            loadInventory();
        };
    });

    document.querySelectorAll(".removeAll").forEach(btn => {
        btn.onclick = async () => {
            await apiPost(`/inventory/remove?item=${btn.dataset.item}&qty=999999`);
            loadInventory();
        };
    });
}

document.getElementById("refreshBtn").onclick = loadInventory;

document.getElementById("clearBtn").onclick = async () => {
    await apiPost("/inventory/clear");
    loadInventory();
};

document.getElementById("addForm").onsubmit = async e => {
    e.preventDefault();
    const f = new FormData(e.target);
    await apiPost(`/inventory/add?item=${f.get("item")}&qty=${f.get("qty")}`);
    loadInventory();
};

loadInventory();
