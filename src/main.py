from fastapi import FastAPI

from src.auth.router import router as auth_router


app = FastAPI(title="Very loaded API")

app.include_router(auth_router)

@app.get("/")
def main():
    "This is main fun"
    return {"message": "Hello from zipURL API."}

