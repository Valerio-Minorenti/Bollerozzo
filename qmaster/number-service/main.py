from fastapi import FastAPI
import redis
import os

app = FastAPI()

# Config Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.get("/")
def root():
    return {"message": "Number Service is running"}

@app.get("/next-number/{queue_id}")
def get_next_number(queue_id: str):
    # Chiave: es. queue:clinica:counter
    key = f"queue:{queue_id}:counter"
    next_number = r.incr(key)
    return {"next": next_number}

