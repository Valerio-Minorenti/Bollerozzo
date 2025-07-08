setInterval(async () => {
    try {
        const res = await fetch("/last-called");
        const data = await res.json();

        if (data.coda && data.numero) {
            document.getElementById("coda").innerText = `Coda: ${data.coda}`;
            document.getElementById("numero").innerText = `Numero: ${data.numero}`;
        }
    } catch (e) {
        console.error("Errore nel recupero dati display:", e);
    }
}, 3000); // aggiorna ogni 3 secondi
