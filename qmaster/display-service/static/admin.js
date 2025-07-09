async function fetchQueuesStatus() {
    try {
        const response = await fetch("/admin/queues");
        const data = await response.json();
        console.log("✅ Dati ricevuti:", data);
        renderQueueTable(data);
    } catch (error) {
        console.error("❌ Errore nel recupero delle code:", error);
    }
}


function renderQueueTable(queues) {
    const tbody = document.querySelector("#code-table tbody");
    tbody.innerHTML = "";  // Pulisce la tabella

    queues.forEach(queue => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${queue.queue_id}</td>
            <td>${queue.ultimo_chiamato}</td>
            <td>${queue.in_attesa.length > 0 ? queue.in_attesa.join(", ") : "-"}</td>
        `;

        tbody.appendChild(row);
    });
}

// Avvia polling ogni 2 secondi
setInterval(fetchQueuesStatus, 2000);
fetchQueuesStatus();  // Prima chiamata immediata
