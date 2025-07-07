import pika
import json
import time

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        coda = data.get("coda")
        numero = data.get("numero_chiamato")
        print(f"📺 DISPLAY >> Coda: {coda} - Numero chiamato: {numero}")
    except Exception as e:
        print(f"[ERRORE] Errore nel parsing messaggio: {e}")

def main():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            channel = connection.channel()
            channel.queue_declare(queue='display', durable=True)
            print("📺 Display Service in ascolto sulla coda 'display'...")
            channel.basic_consume(queue='display', on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("⚠️ RabbitMQ non disponibile. Riprovo tra 3 secondi...")
            time.sleep(3)

if __name__ == "__main__":
    main()
