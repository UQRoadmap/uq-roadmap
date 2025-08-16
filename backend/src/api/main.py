"""Main module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.config import CONFIG
from api.course.routes import router as courses_router
from api.database.service import db_engine, setup_database
from api.degree.routes import router as degree_router
from api.plan.routes import router as plan_router
from common.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Lifespan event handler."""
    configure_logging(CONFIG.log_level)
    await setup_database(db_engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(degree_router, prefix="/degree", tags=["degrees"])
app.include_router(courses_router, prefix="/course", tags=["courses"])
app.include_router(plan_router, prefix="/plan", tags=["plans"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CONFIG.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect_docs() -> RedirectResponse:
    """Redirect base url to docs."""
    return RedirectResponse(url="/docs")
