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
                 `Hai ricevuto il ticket N. ${numero} per la coda "${queue}"`;  // Stringa template corretta
        })
        .catch(error => {
            console.error(error);
            document.getElementById("risultato").innerText =
                "❌ Errore nel recupero del ticket.";
        });
}
