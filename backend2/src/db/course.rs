use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, PgPool, query_as};
use uuid::Uuid;

#[derive(
    Serialize,
    Deserialize,
    Debug,
    JsonSchema,
    sqlx::Type,
    Clone,
    Copy,
)]
#[sqlx(type_name = "course_semester_t")]
pub enum CourseSemester {
    #[serde(rename = "Research Quarter 1")]
    #[sqlx(rename = "Research Quarter 1")]
    Rq1,
    #[serde(rename = "Research Quarter 2")]
    #[sqlx(rename = "Research Quarter 2")]
    Rq2,
    #[serde(rename = "Research Quarter 3")]
    #[sqlx(rename = "Research Quarter 3")]
    Rq3,
    #[serde(rename = "Research Quarter 4")]
    #[sqlx(rename = "Research Quarter 4")]
    Rq4,
    #[serde(rename = "SFC Enrolment Year")]
    #[sqlx(rename = "SFC Enrolment Year")]
    Sfc,
    #[serde(rename = "Semester 1")]
    #[sqlx(rename = "Semester 1")]
    Sem1,
    #[serde(rename = "Semester 2")]
    #[sqlx(rename = "Semester 2")]
    Sem2,
    #[serde(rename = "Summer Semester")]
    #[sqlx(rename = "Summer Semester")]
    Sems,
    #[serde(rename = "Trimester 1")]
    #[sqlx(rename = "Trimester 1")]
    Trim1,
    #[serde(rename = "Trimester 2")]
    #[sqlx(rename = "Trimester 2")]
    Trim2,
    #[serde(rename = "Trimester 3")]
    #[sqlx(rename = "Trimester 3")]
    Trim3,
    #[serde(rename = "UQ College Intake 1")]
    #[sqlx(rename = "UQ College Intake 1")]
    College1,
    #[serde(rename = "UQ College Intake 2")]
    #[sqlx(rename = "UQ College Intake 2")]
    College2,
    #[serde(rename = "Other")]
    #[sqlx(rename = "Other")]
    Other,
}

#[derive(
    Serialize,
    Deserialize,
    JsonSchema,
    sqlx::Type,
    Debug,
    Clone,
    Copy,
)]
#[sqlx(type_name = "course_level_t")]
pub enum CourseLevel {
    #[serde(rename = "undergraduate")]
    #[sqlx(rename = "undergraduate")]
    Undergraduate,
    #[serde(rename = "postgraduate")]
    #[sqlx(rename = "postgraduate")]
    Postgraduate,
    #[serde(rename = "postgraduate coursework")]
    #[sqlx(rename = "postgraduate coursework")]
    PostgraduateCoursework,
    #[serde(rename = "uq college")]
    #[sqlx(rename = "uq college")]
    UqCollege,
    #[serde(rename = "non-award")]
    #[sqlx(rename = "non-award")]
    NonAward,
    #[serde(rename = "other")]
    #[sqlx(rename = "other")]
    Other,
}

#[derive(
    Serialize,
    Deserialize,
    JsonSchema,
    sqlx::Type,
    Debug,
    Clone,
    Copy,
)]
#[sqlx(type_name = "course_mode_t")]
pub enum CourseMode {
    #[serde(rename = "Work Experience")]
    #[sqlx(rename = "Work Experience")]
    WorkExperience,
    #[serde(rename = "In Person")]
    #[sqlx(rename = "In Person")]
    InPerson,
    #[serde(rename = "External")]
    #[sqlx(rename = "External")]
    External,
    #[serde(rename = "Internal")]
    #[sqlx(rename = "Internal")]
    Internal,
    #[serde(rename = "Weekend")]
    #[sqlx(rename = "Weekend")]
    Weekend,
    #[serde(rename = "July Intensive")]
    #[sqlx(rename = "July Intensive")]
    JulyIntensive,
    #[serde(rename = "Off-Shore")]
    #[sqlx(rename = "Off-Shore")]
    OffShore,
    #[serde(rename = "Off-Campus")]
    #[sqlx(rename = "Off-Campus")]
    OffCampus,
    #[serde(rename = "Intensive")]
    #[sqlx(rename = "Intensive")]
    Intensive,
    #[serde(rename = "Web Based")]
    #[sqlx(rename = "Web Based")]
    WebBased,
    #[serde(rename = "Remote")]
    #[sqlx(rename = "Remote")]
    Remote,
    #[serde(rename = "Flexible Delivery")]
    #[sqlx(rename = "Flexible Delivery")]
    Flexible,
}

#[derive(Serialize, Deserialize, Debug, FromRow, Clone)]
pub struct Course {
    pub course_id: Uuid,
    pub category: String,
    pub code: String,
    pub name: String,
    pub description: String,
    pub level: CourseLevel,
    pub num_units: i16,
    pub attendance_mode: CourseMode,
    pub active: bool,
    pub semesters: Vec<CourseSemester>,
}

pub async fn insert(
    db: &PgPool,
    course: &Course,
) -> Result<Course, sqlx::Error> {
    query_as!(
        Course,
        r#"
        INSERT INTO courses
          (course_id, category, code, name, description, level, num_units, attendance_mode, active, semesters)
        VALUES
        ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
        RETURNING
          course_id, category, code, name, description,
          level as "level: _",
          num_units,
          attendance_mode as "attendance_mode: _",
          active,
          semesters as "semesters: _"
        "#,
        course.course_id,
        course.category,
        course.code,
        course.name,
        course.description,
        course.level as _,
        course.num_units,
        course.attendance_mode as _,
        course.active,
        &course.semesters as _
    )
    .fetch_one(db)
    .await
}

pub async fn get_by_category_code(
    db: &PgPool,
    category: &str,
    code: &str,
) -> Result<Option<Course>, sqlx::Error> {
    query_as!(
        Course,
        r#"
        SELECT
          course_id, category, code, name, description,
          level as "level: _",
          num_units,
          attendance_mode as "attendance_mode: _",
          active,
          semesters as "semesters: _"
        FROM courses
        WHERE category = $1 AND code = $2
        "#,
        category,
        code
    )
    .fetch_optional(db)
    .await
}
