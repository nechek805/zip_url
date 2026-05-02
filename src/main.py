from fastapi import FastAPI


app = FastAPI(title="Very loaded API")

@app.get("/")
def main():
    "This is main fun"
    return {"message": "Hello from zipURL API."}

