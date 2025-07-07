# Usa Python come base
FROM python:3.11

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file nell'immagine
COPY . /app

# Installa FastAPI, Uvicorn e Redis client
RUN pip install fastapi uvicorn redis

# Comando per avviare l'app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
