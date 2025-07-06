import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    coda = data.get("coda")
    numero = data.get("numero_chiamato")
    print(f"📢 Coda: {coda} - Numero chiamato: {numero}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    channel.queue_declare(queue='display', durable=True)

    print("🎬 Display Service in ascolto sulla coda 'display'...")
    channel.basic_consume(queue='display', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
