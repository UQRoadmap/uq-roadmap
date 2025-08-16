"""Plans service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.degree.models import DegreeDBModel
from api.plans.model import PlanDBModel
from api.plans.schemas import PlanCreateUpdate


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


async def validate(session: AsyncSession, plan: PlanDBModel) -> None:
    """Validate plan."""
