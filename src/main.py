from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.zip_url.router import router as zip_router, clear_router as clear_zip_router
from src.user.router import router as user_router
from src.core.config import config

app = FastAPI(title="ZIP URL")

origins = config.get_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(zip_router)
app.include_router(clear_zip_router)
app.include_router(user_router)

@app.get("/")
def main():
    "This is main fun"
    return {"message": "Hello from ZIP URL API."}
