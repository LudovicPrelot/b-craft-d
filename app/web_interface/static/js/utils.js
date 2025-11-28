function authHeaders() {
    const token = localStorage.getItem("access_token");
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    };
}

async function apiGet(url) {
    return fetch(url, { headers: authHeaders() }).then(r => r.json());
}

async function apiPost(url, data = null) {
    return fetch(url, {
        method: "POST",
        headers: authHeaders(),
        body: data ? JSON.stringify(data) : null
    }).then(r => r.json());
}
