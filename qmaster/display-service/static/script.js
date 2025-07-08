function aggiornaDisplay() {
    fetch('/last-called')
        .then(response => response.json())
        .then(data => {
            document.getElementById('coda').textContent = data.coda || "---";
            document.getElementById('numero').textContent = data.numero || "--";
        })
        .catch(error => {
            console.error("Errore nel recupero dati:", error);
        });
}

// aggiorna subito all'apertura
aggiornaDisplay();

// aggiorna ogni 2 secondi
setInterval(aggiornaDisplay, 2000);
