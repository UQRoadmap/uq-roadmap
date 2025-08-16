"""Plans service."""

from collections.abc import Awaitable, Callable
from uuid import UUID

from serde.json import from_dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.course.models import CourseDBModel
from api.course.service import get_course_by_full_code
from api.degree.models import DegreeDBModel
from api.degree.service import get_degree
from api.plan.model import PlanDBModel
from api.plan.plan import Plan
from api.plan.schemas import PlanCreateUpdate
from degree.aux_rule import create_ar_from_dict
from degree.degree import Degree
from degree.sr_rule import create_sr_from_dict
from degree.validate_result import ValidateResult


async def get_plans(session: AsyncSession) -> list[PlanDBModel]:
    """Get plan with id."""
    result = await session.execute(select(PlanDBModel))
    return list(result.scalars().unique().all())


async def get_plan(session: AsyncSession, plan_id: UUID) -> PlanDBModel | None:
    """Get plan with id."""
    return await session.get(PlanDBModel, plan_id)


async def create_plan(session: AsyncSession, degree: DegreeDBModel, plan_in: PlanCreateUpdate) -> PlanDBModel:
    """Create a plan."""
    model = PlanDBModel(
        degree=degree,
        name=plan_in.name,
        start_year=plan_in.start_year,
        start_sem=plan_in.start_sem,
        end_year=plan_in.end_year,
        course_dates=plan_in.course_dates,
        course_reqs=plan_in.course_reqs,
        specialisations=plan_in.specialisations,
    )
    session.add(model)
    await session.commit()
    return model


def update_plan(plan: PlanDBModel, degree: DegreeDBModel, plan_in: PlanCreateUpdate) -> PlanDBModel:
    """Update a plan."""
    # Modify the degree
    plan.degree = degree

    # Modify the plan info
    plan.name = plan_in.name
    plan.start_year = plan_in.start_year
    plan.start_sem = plan_in.start_sem
    plan.end_year = plan_in.end_year
    plan.course_dates = plan_in.course_dates
    plan.course_reqs = plan_in.course_reqs
    plan.specialisations = plan_in.specialisations

    return plan


def _get_degree_wrapper(
    session: AsyncSession,
) -> Callable[[str, int], Awaitable[DegreeDBModel | None]]:
    async def func(degree_code: str, year: int) -> DegreeDBModel | None:
        return await get_degree(session, degree_code, year)

    return func


def _get_course_wrapper(
    session: AsyncSession,
) -> Callable[[str], Awaitable[CourseDBModel | None]]:
    async def func(course_code: str) -> CourseDBModel | None:
        return await get_course_by_full_code(session, course_code)

    return func


async def validate_plan(session: AsyncSession, plan_model: PlanDBModel) -> list[ValidateResult]:
    """Validate plan."""
    plan = Plan(
        plan_model.name,
        plan_model.course_dates,
        plan_model.course_reqs,
        plan_model.courses,
        plan_model.degree.degree_code,
        plan_model.specialisations,
    )

    vals = plan_model.degree.details
    pre_sem = vals["sem"]
    sem: int
    if isinstance(pre_sem, str):
        sem = 0 if pre_sem == "" else int(pre_sem)
    elif isinstance(pre_sem, int):
        sem = pre_sem
    else:
        raise Exception("WHAT!!!!")

    vals["sem"] = sem
    degree: Degree = from_dict(Degree, vals)
    if "aux" in vals:
        degree.aux = [create_ar_from_dict(ar_data) for ar_data in vals["aux"]]
    if "srs" in vals:
        degree.srs = [create_sr_from_dict(sr_data) for sr_data in vals["srs"]]

    return degree.validate(plan, _get_course_wrapper(session), _get_degree_wrapper(session))
