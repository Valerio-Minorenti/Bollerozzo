from fastapi import FastAPI
import redis
import os
import requests
import pika
import json

app = FastAPI()

# 🔧 Configurazione Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# 🔧 Configurazione number-service
NUMBER_SERVICE_URL = os.getenv("NUMBER_SERVICE_URL", "http://number-service:8000")

# 🔧 Configurazione RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# 🔌 Connessione a Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


# 📤 Pubblica un messaggio su RabbitMQ
def publish_display_message(queue_id: str, numero: int):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='display', durable=True)

        body = json.dumps({
            "coda": queue_id,
            "numero_chiamato": numero
        })

        channel.basic_publish(
            exchange='',
            routing_key='display',
            body=body
        )

        connection.close()

    except Exception as e:
        print(f"[ERRORE RABBITMQ] {e}")


# ✅ Richiedi un nuovo numero per una specifica coda
@app.post("/queue/{queue_id}/ticket")
def get_ticket(queue_id: str):
    # Chiama il number-service
    response = requests.get(f"{NUMBER_SERVICE_URL}/next-number/{queue_id}")
    ticket = response.json().get("next")

    # Aggiungi alla lista d'attesa in Redis
    r.rpush(f"queue:{queue_id}:waiting_list", ticket)

    return {"ticket": ticket}


# 🔔 Chiama il prossimo numero in coda
@app.post("/queue/{queue_id}/next")
def call_next(queue_id: str):
    next_ticket = r.lpop(f"queue:{queue_id}:waiting_list")
    if next_ticket:
        r.set(f"queue:{queue_id}:last_called", next_ticket)

        # Notifica su Redis Pub/Sub (opzionale)
        r.publish(f"queue:{queue_id}:updates", f"Chiamato numero {next_ticket}")

        # Notifica su RabbitMQ per il display
        publish_display_message(queue_id, next_ticket)

        return {"called": next_ticket}

    return {"message": "Nessun numero in attesa."}


# 📊 Stato corrente della coda
@app.get("/queue/{queue_id}/status")
def queue_status(queue_id: str):
    last_called = r.get(f"queue:{queue_id}:last_called") or "Nessuno"
    waiting = r.lrange(f"queue:{queue_id}:waiting_list", 0, -1)
    return {
        "ultimo_numero_chiamato": last_called,
        "in_attesa": waiting
    }


# 🔍 Test base (opzionale)
@app.get("/")
def read_root():
    return {"message": "Queue Service is running"}
