"""Course data transformers."""

import datetime
import logging

from api.course.models import CourseDBModel, CourseOfferingDBModel, CourseSecatDBModel, CourseSecatQuestionsDBModel
from common.enums import CourseMode
from common.reqs_parsing import parse_requirement
from common.schemas import SecatInfo
from scraper.courses.models import ScrapedCourse, ScrapedCourseOffering

log = logging.getLogger(__name__)

ASSESSMENT_ITEMS_KEY = "items"

CURRENT_YEAR = datetime.datetime.now(datetime.UTC).year
COURSE_ACTIVE_BUFFER = 2  # courses must run within 2 years to be considered active


def _transform_scraped_secat(scraped: SecatInfo) -> CourseSecatDBModel:
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
        num_enrolled=scraped.num_enrolled,
        num_responses=scraped.num_responses,
        response_rate=scraped.response_rate,
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

    recent_offerings = [o for o in offerings if offerings if o.year >= CURRENT_YEAR - COURSE_ACTIVE_BUFFER]
    unique_sems = {o.semester_enum for o in recent_offerings}

    semesters_str = None if len(unique_sems) == 0 else ",".join(str(sem) for sem in unique_sems)

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
        active=len(recent_offerings) != 0,
        semesters_str=semesters_str,
        faculty=scraped.faculty,
        faculty_url=scraped.faculty_url,
        school=scraped.school,
        duration=scraped.duration,
        class_hours=scraped.class_hours,
        course_enquries=scraped.course_enquries,
        offerings=offerings,
        secat=_transform_scraped_secat(scraped.secat) if scraped.secat else None,
        assessment={ASSESSMENT_ITEMS_KEY: [a.model_dump(mode="python") for a in scraped.latest_assessment]}
        if scraped.latest_assessment
        else None,
    )
