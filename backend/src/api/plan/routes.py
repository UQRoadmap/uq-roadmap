"""Plan routes."""

import asyncio
import logging
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from serde import to_dict

from api.database.deps import DbSession
from api.degree.schemas import DegreeRead
from api.degree.service import get_degree_by_id
from api.plan.model import PlanDBModel
from api.plan.schemas import PlanCreateUpdate, PlanRead
from api.plan.service import create_plan, get_plan, get_plans, update_plan, validate_plan

if TYPE_CHECKING:
    from degree.validate_result import ValidateResult

r = router = APIRouter()

log = logging.getLogger(__name__)


async def add_validation(session: DbSession, plan: PlanDBModel) -> PlanRead:
    """Add validation to plan db."""
    result = PlanRead(
        plan_id=plan.plan_id,
        degree=DegreeRead(
            degree_id=plan.degree.degree_id,
            degree_code=plan.degree.degree_code,
            year=plan.degree.year,
            title=plan.degree.title,
        ),
        name=plan.name,
        start_year=plan.start_year,
        start_sem=plan.start_sem,
        course_dates=plan.course_dates,
        course_reqs=plan.course_reqs,
        specialisations=plan.specialisations,
        courses=plan.courses,
        validation_results=None,
    )

    validation_results: list[ValidateResult] | None = None
    try:
        validation_results = await validate_plan(session, plan)
        result.validation_results = validation_results
    except Exception:
        log.exception(f"Unable to get validation results for plan {plan.plan_id}")
    return result


@r.get("")
async def get_all(db: DbSession) -> list[PlanRead]:
    """Get all plans."""
    plans = await get_plans(db)
    result = [add_validation(db, plan) for plan in plans]
    return await asyncio.gather(*result)


@r.get("/{plan_id}")
async def get(db: DbSession, plan_id: UUID) -> PlanRead:
    """Endpoint to get a plan."""
    plan = await get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan under id '{plan_id}' could not be found."
        )

    return await add_validation(db, plan)


@r.post("", response_model=PlanRead)
async def create(db: DbSession, plan_in: PlanCreateUpdate) -> PlanDBModel:
    """Create a plan."""
    degree = await get_degree_by_id(db, plan_in.degree_id)
    if degree is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The degree with the id '{plan_in.degree_id}' can not be found",
        )

    try:
        return await create_plan(db, degree, plan_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The provided start year is after the provided end year."
        ) from e


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
