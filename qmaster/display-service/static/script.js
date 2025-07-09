async function fetchQueues() {
    try {
        const response = await fetch("http://localhost:5000/queues/status");
        const data = await response.json();
        renderTable(data);
    } catch (error) {
        console.error("Errore nel recupero delle code:", error);
    }
}

function renderTable(queues) {
    const tbody = document.querySelector("#code-table tbody");
    tbody.innerHTML = "";

    queues.forEach(queue => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${queue.queue_id}</td>
            <td>${queue.ultimo_chiamato}</td>
            <td>${queue.in_attesa.join(", ") || "-"}</td>
        `;

        tbody.appendChild(row);
    });
}

setInterval(fetchQueues, 2000); // Aggiorna ogni 2 secondi
fetchQueues(); // Chiamata iniziale
