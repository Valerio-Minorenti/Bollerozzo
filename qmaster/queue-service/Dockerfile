FROM python:3.11-slim

WORKDIR /app

# Installa le dipendenze da requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il contenuto nella cartella /app del container
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt
COPY ./templates ./templates
COPY ./static ./static   # Solo se esiste


# Avvia il servizio FastAPI sulla porta 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
