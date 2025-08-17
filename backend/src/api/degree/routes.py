"""Routes for degrees."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from api.database.deps import DbSession
from api.degree.models import DegreeDBModel
from api.degree.schemas import DegreeRead, DegreeSummary
from api.degree.service import get_all_degrees, get_degree, get_degree_by_id, get_degrees_summary

r = router = APIRouter()


@r.get("", response_model=list[DegreeRead])
async def get_many(session: DbSession) -> list[DegreeDBModel]:
    """Get all the degrees."""
    return await get_all_degrees(session)


@r.get("/summary")
async def get_summary(session: DbSession) -> list[DegreeSummary]:
    """Get all the degrees."""
    return await get_degrees_summary(session)


@r.get("/simple", response_model=DegreeRead)
async def get_one_simple(degree_code: str, year: int, session: DbSession) -> DegreeDBModel:
    """Get a single degree."""
    result = await get_degree(session, str(degree_code), year)
    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Degree with the code {degree_code} and year {year} could not be found"
        )
    return result


@r.get("/{degree_id}", response_model=DegreeRead)
async def get_one(degree_id: UUID, session: DbSession) -> DegreeDBModel:
    """Get a single degree."""
    result = await get_degree_by_id(session, degree_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Degree under the id '{degree_id}' could not be found")
    return result
