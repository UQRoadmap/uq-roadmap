use axum::{Json, Router, http::StatusCode, response::IntoResponse, routing::get};
use serde::{Deserialize, Serialize};
use tracing::{debug, info};
use uuid::Uuid;

#[tokio::main]
async fn main() {
    // Enable logging:
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();
    info!("Test log");

    let app = app();

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();

    debug!("Listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}

fn app() -> Router {
    Router::new()
        .route("/", get(test))
        .route("/course", get(get_course))
}

#[derive(Serialize, Deserialize)]
struct Response {
    magic: String,
}
#[derive(Serialize, Deserialize, Debug)]
enum CourseSemester {
    #[serde(rename = "Research Quarter 1")]
    RQ1,
    #[serde(rename = "Research Quarter 2")]
    RQ2,
    #[serde(rename = "Research Quarter 3")]
    RQ3,
    #[serde(rename = "Research Quarter 4")]
    RQ4,
    #[serde(rename = "SFC Enrolment Year")]
    SFC,
    #[serde(rename = "Semester 1")]
    SEM1,
    #[serde(rename = "Semester 2")]
    SEM2,
    #[serde(rename = "Summer Semester")]
    SEMS,
    #[serde(rename = "Trimester 1")]
    TRIM1,
    #[serde(rename = "Trimester 2")]
    TRIM2,
    #[serde(rename = "Trimester 3")]
    TRIM3,
    #[serde(rename = "UQ College Intake 1")]
    COLLEGE1,
    #[serde(rename = "UQ College Intake 2")]
    COLLEGE2,
    #[serde(rename = "Other")]
    OTHER,
}

#[derive(Serialize, Deserialize)]
enum CourseLevel {
    #[serde(rename = "undergraduate")]
    Undergraduate,
    #[serde(rename = "postgraduate")]
    Postgraduate,
    #[serde(rename = "postgraduate coursework")]
    PostgraduateCoursework,
    #[serde(rename = "uq college")]
    UQCollege,
    #[serde(rename = "non-award")]
    NonAward,
    #[serde(rename = "other")]
    OTHER,
}

#[derive(Serialize, Deserialize)]
enum CourseMode {
    #[serde(rename = "Work Experience")]
    WorkExperience,
    #[serde(rename = "In Person")]
    InPerson,
    #[serde(rename = "External")]
    External,
    #[serde(rename = "Internal")]
    Internal,
    #[serde(rename = "Weekend")]
    Weekend,
    #[serde(rename = "July Intensive")]
    JulyIntensive,
    #[serde(rename = "Off-Shore")]
    OffShore,
    #[serde(rename = "Off-Campus")]
    OffCampus,
    #[serde(rename = "Intensive")]
    Intensive,
    #[serde(rename = "Web Based")]
    WebBased,
    #[serde(rename = "Remote")]
    Remote,
    #[serde(rename = "Flexible Delivery")]
    Flexible,
}

#[derive(Serialize, Deserialize)]
struct CourseResponse {
    course_id: Uuid,
    category: String,
    code: String,
    name: String,
    description: String,
    level: CourseLevel,
    num_units: u8,
    attendance_mode: CourseMode,
    active: bool,
    semesters: Vec<CourseSemester>,
}

async fn test() -> impl IntoResponse {
    let response = Response {
        magic: "Hello".to_string(),
    };
    (StatusCode::OK, Json(response))
}

async fn get_course() -> impl IntoResponse {
    let response = CourseResponse {
        course_id: Uuid::new_v4(),
        category: "CSSE".to_string(),
        code: "2310".to_string(),
        name: "Computer Systems Principles and Programming".to_string(),
        description: "CSSE2310 is an introduction to UNIX (Linux), the principles of computer systems (networks and operating systems) and systems programming in C.".to_string(),
        level: CourseLevel::Undergraduate,
        num_units: 2,
        attendance_mode: CourseMode::Internal,
        active: true,
        semesters: vec![CourseSemester::SEM1, CourseSemester::SEM2]
    };
    (StatusCode::OK, Json(response))
}
