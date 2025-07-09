FROM python:3.11-slim

WORKDIR /app

# Copia i file prima di installare requirements per caching più efficiente
COPY requirements.txt .

# Installa le dipendenze (inclusa redis)
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice sorgente
COPY . .

# Comando di avvio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
