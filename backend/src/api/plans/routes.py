"""Plan routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from serde import to_dict

from api.database.deps import DbSession
from api.degree.service import get_degree_by_id
from api.plans.model import PlanDBModel
from api.plans.schemas import PlanCreateUpdate, PlanRead
from api.plans.service import create_plan, get_plan, update_plan, validate_plan

r = router = APIRouter()


@r.get("/{plan_id}", response_model=PlanRead)
async def get(db: DbSession, plan_id: UUID) -> PlanDBModel:
    """Endpoint to get a plan."""
    plan = await get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan under id '{plan_id}' could not be found."
        )

    return plan


@r.post("", response_model=PlanRead)
async def create(db: DbSession, plan_in: PlanCreateUpdate) -> PlanDBModel:
    """Create a plan."""
    degree = await get_degree_by_id(db, plan_in.degree_id)
    if degree is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The degree with the id '{plan_in.degree_id}' can not be found",
        )

    return await create_plan(db, degree, plan_in)


@r.put("/{plan_id}", response_model=PlanRead)
async def update(db: DbSession, plan_in: PlanCreateUpdate, plan_id: UUID) -> PlanDBModel:
    """Update a plan."""
    plan = await get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan under id '{plan_id}' could not be found."
        )

    degree = await get_degree_by_id(db, plan_in.degree_id)
    if degree is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The degree with the id '{plan_in.degree_id}' can not be found",
        )

    return update_plan(plan, degree, plan_in)


@r.put("/{plan_id}/validate")
async def validate(db: DbSession, plan_id: UUID) -> list[dict]:
    """Validate a plan."""
    plan_model = await get_plan(db, plan_id)
    if plan_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan under id '{plan_id}' could not be found."
        )

    result = await validate_plan(db, plan_model)
    return [to_dict(r) for r in result]
