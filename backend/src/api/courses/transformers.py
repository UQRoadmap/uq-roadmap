"""Course data transformers."""

import logging

from api.courses.models import CourseDBModel, CourseOfferingDBModel, CourseSecatDBModel, CourseSecatQuestionsDBModel
from common.enums import CourseMode
from common.reqs_parsing import parse_requirement
from scraper.courses.models import ScrapedCourse, ScrapedCourseOffering, ScrapedSecatInfo

log = logging.getLogger(__name__)


def _transform_scraped_secat(scraped: ScrapedSecatInfo) -> CourseSecatDBModel:
    # hopefully when they're linked up to the course the pk will be identified
    return CourseSecatDBModel(
        questions=[
            CourseSecatQuestionsDBModel(
                name=question.name,  # hopefully secat_id will sort itself out
                s_agree=question.s_agree,
                agree=question.agree,
                middle=question.middle,
                disagree=question.disagree,
                s_disagree=question.s_disagree,
            )
            for question in scraped.questions
        ],
    )


def _transform_scraped_offering(scraped: ScrapedCourseOffering, active: bool) -> CourseOfferingDBModel:  # noqa: FBT001
    """Transforms a scraped course offering into a db model."""
    year = int(scraped.semester.replace(" ", "").split(",")[1][:4])

    return CourseOfferingDBModel(
        year=year,
        semester=scraped.semester,
        location=scraped.location,
        mode=CourseMode(scraped.mode),
        profile_url=scraped.profile_url,
        active=active,
    )


def transform_scraped_course(scraped: ScrapedCourse) -> CourseDBModel:
    """Transform scraped course into db model."""
    category, code = scraped.code_parts
    log.info(f"Transforming course: {scraped.code}")

    incompatible_req = parse_requirement(scraped.incompatible) if scraped.incompatible else None
    prerequisite_req = parse_requirement(scraped.prerequisite) if scraped.prerequisite else None

    offerings: list[CourseOfferingDBModel] = []

    offerings = [_transform_scraped_offering(offering, True) for offering in scraped.current_offerings]  # noqa: FBT003

    offerings.extend(_transform_scraped_offering(offering, False) for offering in scraped.archived_offerings)  # noqa: FBT003

    return CourseDBModel(
        category=category,
        code=code,
        name=scraped.name,
        description=scraped.description,
        level=scraped.level,
        num_units=scraped.num_units,
        incompatible=incompatible_req.model_dump(mode="python") if incompatible_req else None,
        prerequisite=prerequisite_req.model_dump(mode="python") if prerequisite_req else None,
        attendance_mode=CourseMode(scraped.attendance_mode),
        faculty=scraped.faculty,
        faculty_url=scraped.faculty_url,
        school=scraped.school,
        duration=scraped.duration,
        class_hours=scraped.class_hours,
        course_enquries=scraped.course_enquries,
        offerings=offerings,
        secat=_transform_scraped_secat(scraped.secat) if scraped.secat else None,
        assessment={"assessment": [a.model_dump(mode="python") for a in scraped.latest_assessment]}
        if scraped.latest_assessment
        else None,
    )
