document.addEventListener("DOMContentLoaded", function () {
    fetch("/queues")
        .then(response => {
            if (!response.ok) throw new Error("Errore nel caricamento sportelli");
            return response.json();
        })
        .then(queues => {
            const select = document.getElementById("queue");
            select.innerHTML = "";

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

    fetch(`/queue/${queue}/ticket`, {
        method: "POST"
    })
        .then(response => {
            if (!response.ok) throw new Error("Errore durante la richiesta del ticket");
            return response.json();
        })
        .then(data => {
            document.getElementById("risultato").innerText =
                `✅ ${data.message}`;
        })
        .catch(error => {
            console.error(error);
            document.getElementById("risultato").innerText =
                "❌ Errore nella richiesta del ticket.";
        });
}
