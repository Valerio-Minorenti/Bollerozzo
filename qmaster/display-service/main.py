from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pika
import json
import threading
import os
import time
import requests

# 🔧 Configurazione ambiente
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_SERVICE_URL = os.getenv("QUEUE_SERVICE_URL", "http://queue-service:8000")

# 🚀 Avvia l'app FastAPI
app = FastAPI()

# 📂 Statici e template
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 💾 Stato numero corrente aggiornato da RabbitMQ
latest_data = {"coda": "---", "numero": "---"}

# 🌐 Pagina display pubblica
@app.get("/", response_class=HTMLResponse)
def display_page(request: Request):
    return templates.TemplateResponse("display.html", {"request": request})

# 🔁 Polling per display pubblico
@app.get("/last-called", response_class=JSONResponse)
def get_last_called():
    return latest_data

# 🧠 Pagina pannello admin HTML
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# 📊 API proxy per stato delle code (proxy a queue-service)
@app.get("/admin/queues", response_class=JSONResponse)
def admin_queues_status():
    try:
        response = requests.get(f"{QUEUE_SERVICE_URL}/queues/status", timeout=3)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": f"Errore dal queue-service: {e}"})


# 🔔 RabbitMQ consumer
def consume_rabbit():
    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            latest_data["coda"] = data.get("coda", "---")
            latest_data["numero"] = data.get("numero_chiamato", "---")
            print(f"📺 DISPLAY >> Coda: {latest_data['coda']} | Numero: {latest_data['numero']}")
        except Exception as e:
            print(f"[ERRORE] Errore parsing messaggio: {e}")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
            )
            channel = connection.channel()
            channel.queue_declare(queue='display', durable=True)
            print("✅ DISPLAY >> In ascolto su RabbitMQ...")
            channel.basic_consume(queue='display', on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except Exception as e:
            print(f"⚠️ Errore connessione RabbitMQ: {e}. Riprovo tra 3 secondi...")
            time.sleep(3)

# 🔄 Avvia RabbitMQ listener in thread separato
threading.Thread(target=consume_rabbit, daemon=True).start()
