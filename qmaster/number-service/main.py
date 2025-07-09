from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
import os

app = FastAPI()

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Static & HTML templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home():
    return {"message": "Number Service is running"}

@app.get("/ticket", response_class=HTMLResponse)
def ticket_page(request: Request):
    return templates.TemplateResponse("ticket.html", {"request": request})

@app.get("/next-number/{queue_id}")
def get_next_number(queue_id: str):
    next_number = r.incr(f"queue:{queue_id}")
    return {"next": next_number}

@app.get("/queues")
def get_available_queues():
    # Recupera tutte le chiavi Redis che rappresentano le code
    keys = r.keys("queue:*")
    queues = [key.split("queue:")[1] for key in keys]
    return JSONResponse(content=queues)
