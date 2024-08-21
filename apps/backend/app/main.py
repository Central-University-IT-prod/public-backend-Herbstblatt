from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import tortoise

from .routers import registration, points, notes
from db import tortoise_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    await tortoise.Tortoise.init(tortoise_config)
    yield
    await tortoise.Tortoise.close_connections()


app = FastAPI(root_path="/api", lifespan=lifespan)
app.include_router(registration.router)
app.include_router(points.router)
app.include_router(notes.router)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/ping")
def ping():
    return "pong"
