document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("dispatcher-test-form");
    const resultBox = document.getElementById("test-result");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const endpoint = document.getElementById("endpoint").value;
        const method = document.getElementById("method").value;

        resultBox.textContent = "Exécution…";

        try {
            const res = await fetch(`/api/admin/dispatcher/test?endpoint=${encodeURIComponent(endpoint)}&method=${method}`);
            const data = await res.json();

            resultBox.textContent = JSON.stringify(data, null, 2);
        } catch (err) {
            resultBox.textContent = "Erreur: " + err;
        }
    });
});
