"""Plan routes."""

from fastapi import APIRouter

r = router = APIRouter()


@r.get("")
async def get() -> None:
    pass
