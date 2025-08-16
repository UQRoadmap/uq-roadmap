"""Course routes."""

from fastapi import APIRouter, HTTPException, status

from api.courses.models import CourseDBModel
from api.courses.schemas import CourseRead, CourseReadDetailed
from api.courses.service import get_all_courses, get_course_by_full_code
from api.database.deps import DbSession
from common.enums import CourseLevel

r = router = APIRouter()


@r.get("", response_model=list[CourseRead])
async def get_all(
    db: DbSession,
    course_category: str | None = None,
    course_level: CourseLevel | None = None,
    num_units: int | None = None,
    is_active: bool | None = None,  # noqa: FBT001
) -> list[CourseDBModel]:
    """Get all courses."""
    return await get_all_courses(db, course_category, course_level, num_units, is_active)


@r.get("/{course_code}", response_model=CourseReadDetailed)
async def get(course_code: str, db: DbSession) -> CourseDBModel:
    """Get a course by ID."""
    result = await get_course_by_full_code(db, course_code)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course under the id '{course_code}' not found"
        )
    return result
