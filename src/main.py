from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.celery_app.celery_send_email import send_confirm_email

app = FastAPI(title="ZIP URL")

app.include_router(auth_router)

@app.get("/")
def main():
    "This is main fun"
    return {"message": "Hello from ZIP URL API."}
