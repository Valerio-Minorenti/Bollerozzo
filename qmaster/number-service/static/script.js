document.addEventListener("DOMContentLoaded", function () {
    // Carica dinamicamente gli sportelli attivi
    fetch("/queues")
        .then(response => {
            if (!response.ok) throw new Error("Errore nel caricamento sportelli");
            return response.json();
        })
        .then(queues => {
            const select = document.getElementById("queue");
            select.innerHTML = ""; // Pulisce le opzioni

            queues.forEach(queue => {
                const option = document.createElement("option");
                option.value = queue;
                option.textContent = queue;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Errore nel caricamento sportelli:", error);
            const select = document.getElementById("queue");
            select.innerHTML = "<option disabled>Errore nel caricamento</option>";
        });
});

function richiediTicket() {
    const queue = document.getElementById("queue").value;

    fetch(`/next-number/${queue}`)
        .then(response => {
            if (!response.ok) throw new Error("Errore nella richiesta");
            return response.json();
        })
        .then(data => {
            const numero = data.next;
            document.getElementById("risultato").innerText =
                 `Hai ricevuto il ticket N. ${numero} per la coda "${queue}"`;
        })
        .catch(error => {
            console.error(error);
            document.getElementById("risultato").innerText =
                "❌ Errore nel recupero del ticket.";
        });
}
