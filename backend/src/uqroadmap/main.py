"""Main module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from uqroadmap.database.logger import configure_logging
from uqroadmap.database.service import db_engine, initialise_database
from uqroadmap.degree.routes import router as degree_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Lifespan event handler."""
    configure_logging()
    await initialise_database(db_engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(degree_router, prefix="/degrees", tags=["degrees"])


@app.get("/")
async def redirect_docs() -> RedirectResponse:
    """Redirect base url to docs."""
    return RedirectResponse(url="/docs")
