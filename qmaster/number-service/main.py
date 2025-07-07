from fastapi import FastAPI

app = FastAPI()

# Dizionario per tenere traccia dei numeri per ciascuna coda
counters = {}

@app.get("/")
def root():
    return {"message": "Number Service is running"}

@app.get("/next-number/{queue_id}")
def next_number(queue_id: str):
    if queue_id not in counters:
        counters[queue_id] = 1
    else:
        counters[queue_id] += 1
    return {"next": counters[queue_id]}
