"""Routes for degrees."""

from fastapi import APIRouter, HTTPException, status

from uqroadmap.database.deps import DbSession
from uqroadmap.degree.models import DegreeDBModel
from uqroadmap.degree.schemas import DegreeCreate, DegreeRead
from uqroadmap.degree.service import create_degree, get_all_degrees, get_degree_by_id

r = router = APIRouter()


@r.get("", response_model=list[DegreeRead])
async def get_many(session: DbSession) -> list[DegreeDBModel]:
    """Get all the degrees."""
    return await get_all_degrees(session)


@r.get("/{degree_id}", response_model=DegreeRead)
async def get_one(degree_id: int, session: DbSession) -> DegreeDBModel:
    """Get a single degree."""
    result = await get_degree_by_id(session, degree_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Degree under the id '{degree_id}' could not be found")
    return result


@r.post("", response_model=DegreeRead, status_code=status.HTTP_201_CREATED)
async def create(degree_in: DegreeCreate, session: DbSession) -> DegreeDBModel:
    """Create a degree."""
    existing = await get_degree_by_id(session, degree_in.degree_id)
    if existing is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Degree under the id '{degree_in.degree_id}' already exists")

    return await create_degree(session, degree_in)
