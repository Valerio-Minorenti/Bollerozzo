from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import redis
import os
import requests
import pika
import json
import logging

app = FastAPI()

# 📦 Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("queue-service")

# 🔧 Configurazione Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# 🔧 Configurazione number-service
NUMBER_SERVICE_URL = os.getenv("NUMBER_SERVICE_URL", "http://number-service:8000")

# 🔧 Configurazione RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

# 🔌 Connessione a Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


# 📤 Pubblica un messaggio su RabbitMQ
def publish_display_message(queue_id: str, numero: int):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        channel.queue_declare(queue='display', durable=True)

        message = {
            "coda": queue_id,
            "numero_chiamato": numero
        }

        channel.basic_publish(
            exchange='',
            routing_key='display',
            body=json.dumps(message)
        )

        connection.close()
        logger.info(f"📢 Messaggio inviato al display: {message}")

    except Exception as e:
        logger.error(f"[ERRORE RABBITMQ] {e}")


# ✅ Crea una nuova coda (opzionale)
@app.post("/queue/{queue_id}/create")
def create_queue(queue_id: str):
    r.delete(f"queue:{queue_id}:waiting_list")
    r.set(f"queue:{queue_id}:last_called", 0)
    return {"message": f"Coda '{queue_id}' creata"}


# 🎟️ Richiedi un nuovo numero per una coda
@app.post("/queue/{queue_id}/ticket")
def get_ticket(queue_id: str):
    try:
        response = requests.get(f"{NUMBER_SERVICE_URL}/next-number/{queue_id}", timeout=2)
        response.raise_for_status()
        ticket = response.json().get("next")
    except requests.RequestException as e:
        logger.error(f"[ERRORE] Errore contattando number-service: {e}")
        raise HTTPException(status_code=502, detail="Errore nel servizio numeri.")

    if ticket is None:
        raise HTTPException(status_code=500, detail="Risposta non valida dal number-service.")

    r.rpush(f"queue:{queue_id}:waiting_list", ticket)
    logger.info(f"🎟️ Numero {ticket} assegnato alla coda '{queue_id}'")
    return {"ticket": ticket}


# 🔔 Chiama il prossimo numero
@app.post("/queue/{queue_id}/next")
def call_next(queue_id: str):
    next_ticket = r.lpop(f"queue:{queue_id}:waiting_list")
    if next_ticket:
        r.set(f"queue:{queue_id}:last_called", next_ticket)

        # Notifica su Redis Pub/Sub (opzionale)
        r.publish(f"queue:{queue_id}:updates", f"Chiamato numero {next_ticket}")

        # Notifica display via RabbitMQ
        publish_display_message(queue_id, next_ticket)

        logger.info(f"📞 Numero {next_ticket} chiamato per la coda '{queue_id}'")
        return {"called": next_ticket}

    return JSONResponse(status_code=204, content={"message": "Nessun numero in attesa."})


# 📊 Stato della coda
@app.get("/queue/{queue_id}/status")
def queue_status(queue_id: str):
    last_called = r.get(f"queue:{queue_id}:last_called") or "Nessuno"
    waiting = r.lrange(f"queue:{queue_id}:waiting_list", 0, -1)
    return {
        "ultimo_numero_chiamato": last_called,
        "in_attesa": waiting
    }


# 🔍 Test di base
@app.get("/")
def read_root():
    return {"message": "✅ Queue Service is running"}
