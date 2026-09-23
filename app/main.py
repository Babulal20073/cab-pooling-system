from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.init_db import init_db
from app.routers import health, auth, bookings, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    yield


app = FastAPI(
    title="Cab Pooling & Smart Pickup Routing",
    lifespan=lifespan,
)