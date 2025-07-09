async function updateDisplay() {
    try {
        const response = await fetch("/last-called");
        const data = await response.json();

        document.getElementById("coda").textContent = data.coda || "---";
        document.getElementById("numero").textContent = data.numero || "--";
    } catch (error) {
        console.error("❌ Errore nel recupero del numero:", error);
    }
}

// Avvia aggiornamento ogni 2 secondi
setInterval(updateDisplay, 2000);
updateDisplay();  // Primo aggiornamento subito
