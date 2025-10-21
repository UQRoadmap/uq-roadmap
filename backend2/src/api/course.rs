use axum::routing::get;
use axum::{Router, extract::State};

use crate::AppState;
use crate::db;
use crate::db::course_details::CourseDetails;
use axum::response::IntoResponse;
use axum::{Json, extract::Path, http::StatusCode};
pub fn router() -> Router<AppState> {
    return Router::new()
        .route("/{category}/{code}", get(get_course_by_pair))
        .route("/{category}", get(get_courses_by_category));
}

#[utoipa::path(
    get,
    path = "/course/{category}/{code}",
    tag = "course",
    responses(
        (status = 200, description = "Gets a course by its category and code", body = CourseDetails),
    ),
)]
async fn get_course_by_pair(
    State(AppState { db, .. }): State<AppState>,
    Path((category, code)): Path<(String, String)>,
) -> impl IntoResponse {
    match db::course_details::get_by_category_code(&db, &category, &code).await {
        Ok(Some(c)) => (StatusCode::OK, Json(c)).into_response(),
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({"error": "not found"})),
        )
            .into_response(),
        Err(e) => {
            tracing::error!(error = ?e, "db error");
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "internal"})),
            )
                .into_response()
        }
    }
}

#[utoipa::path(get, path = "/course/{category}", tag = "course", responses())]
async fn get_courses_by_category(
    State(AppState { db, .. }): State<AppState>,
    Path(category): Path<String>,
) -> impl IntoResponse {
    match db::course_details::get_all_by_category(&db, &category).await {
        Ok(cs) => (StatusCode::OK, Json(cs)).into_response(),
        Err(e) => {
            tracing::error!(error = ?e, "db error");
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "internal"})),
            )
                .into_response()
        }
    }
}
