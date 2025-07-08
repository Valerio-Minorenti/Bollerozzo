from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pika
import json
import threading

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

latest_data = {"coda": "---", "numero": "---"}

@app.get("/", response_class=HTMLResponse)
def display_page(request: Request):
    return templates.TemplateResponse("display.html", {"request": request})

@app.get("/last-called")
def get_last_called():
    return latest_data

def consume_rabbit():
    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            latest_data["coda"] = data.get("coda", "---")
            latest_data["numero"] = data.get("numero_chiamato", "---")
            print(f"📺 DISPLAY >> {latest_data}")
        except Exception as e:
            print(f"[ERRORE] Errore parsing messaggio: {e}")

    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            channel = connection.channel()
            channel.queue_declare(queue='display', durable=True)
            channel.basic_consume(queue='display', on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except Exception:
            import time
            print("⚠️ RabbitMQ non disponibile. Riprovo tra 3 secondi...")
            time.sleep(3)

# Avvia il listener RabbitMQ in un thread separato
threading.Thread(target=consume_rabbit, daemon=True).start()
