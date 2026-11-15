from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from .api import auth, products
from .db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast if the database is unreachable
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth.router)
app.include_router(products.router)
