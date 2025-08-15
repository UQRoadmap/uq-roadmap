"""Main module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api.config import CONFIG
from api.database.service import db_engine, initialise_database
from api.degree.routes import router as degree_router
from common.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Lifespan event handler."""
    configure_logging(CONFIG.log_level)
    await initialise_database(db_engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(degree_router, prefix="/degrees", tags=["degrees"])


@app.get("/")
async def redirect_docs() -> RedirectResponse:
    """Redirect base url to docs."""
    return RedirectResponse(url="/docs")
