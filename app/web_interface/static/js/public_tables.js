async function loadPublicTable(apiUrl, tableId, transformFn) {
    const res = await fetch(apiUrl);
    const data = await res.json();
    const tbody = document.querySelector(`#${tableId} tbody`);
    tbody.innerHTML = "";

    const list = Object.values(data)[0]; // ingredients/recipes/professions

    list.forEach(item => {
        const row = transformFn(item);
        const tr = document.createElement("tr");
        Object.keys(row).forEach(col => {
            const td = document.createElement("td");
            td.textContent = row[col];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}
