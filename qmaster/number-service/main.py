from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import pika

# Connessione a RabbitMQ
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Dichiarazione delle code che ti servono
channel.queue_declare(queue="sportello1", durable=True)
channel.queue_declare(queue="display", durable=True)

app = FastAPI()

# Configurazione dinamica host/porta del number-service
NUMBER_SERVICE_HOST = os.getenv("NUMBER_SERVICE_HOST", "localhost")
NUMBER_SERVICE_PORT = os.getenv("NUMBER_SERVICE_PORT", "8000")

# Modello per ricevere input
class QueueRequest(BaseModel):
    queue_id: str

# Test base
@app.get("/")
def root():
    return {"message": "Queue Service is running"}

# Richiesta di ticket
@app.post("/ticket")
def take_ticket(data: QueueRequest):
    try:
        # Chiamata al number-service
        response = requests.get(
            f"http://{NUMBER_SERVICE_HOST}:{NUMBER_SERVICE_PORT}/next-number/{data.queue_id}"
        )
        response.raise_for_status()
        ticket_number = response.json()["next"]
    except Exception as e:
        return {"error": f"Errore nel contattare number-service: {str(e)}"}

    # Pubblica su RabbitMQ
    channel.basic_publish(
    exchange="",
    routing_key=data.queue_id,  # es: "sportello1"
    body=str(ticket_number)
)

    return {"queue": data.queue_id, "ticket": ticket_number}

