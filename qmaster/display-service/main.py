import pika
import json
import time
import threading
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()
clients = []

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Display</title>
</head>
<body>
    <h1>Numero chiamato</h1>
    <h2 id="numero">In attesa...</h2>
    <script>
        const ws = new WebSocket("ws://" + location.host + "/ws");
        ws.onmessage = (event) => {
            document.getElementById("numero").innerText = event.data;
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def index():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # usato solo per mantenere aperta la connessione
    except:
        clients.remove(websocket)

def notify_clients(message: str):
    for client in clients:
        try:
            import asyncio
            asyncio.create_task(client.send_text(message))
        except Exception as e:
            print(f"[ERRORE INVIO WEBSOCKET] {e}")

def rabbit_listener():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            channel = connection.channel()
            channel.queue_declare(queue='display', durable=True)

            print("📺 Display in ascolto su 'display'...")

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    coda = data.get("coda")
                    numero = data.get("numero_chiamato")
                    msg = f"Coda {coda}: Numero {numero}"
                    print(f"📺 {msg}")
                    notify_clients(msg)
                except Exception as e:
                    print(f"[ERRORE PARSING] {e}")

            channel.basic_consume(queue='display', on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("⚠️ RabbitMQ non disponibile. Riprovo tra 3s...")
            time.sleep(3)

# Avvia il thread consumer RabbitMQ
threading.Thread(target=rabbit_listener, daemon=True).start()
