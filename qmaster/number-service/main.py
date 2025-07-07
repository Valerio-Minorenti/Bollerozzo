from fastapi import FastAPI
import redis
import os

app = FastAPI()

redis_host = os.getenv("REDIS_HOST", "redis")  # usa il nome del servizio Docker
redis_port = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


@app.get("/")
def root():
    return {"message": "Number Service is running"}

@app.get("/next-number/{queue_id}")
def get_next_number(queue_id: str):
    # Incrementa il numero del ticket per la coda specifica
    next_number = r.incr(f"queue:{queue_id}")
    return {"next": next_number}
