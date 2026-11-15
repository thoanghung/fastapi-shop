from fastapi import FastAPI
from .api import auth

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth.router)