mod openapi;

use crate::AppState;
use crate::db;
use crate::db::course::Course;
use axum::Router;
use axum::response::IntoResponse;
use axum::routing::get;
use axum::{
    Json,
    extract::{Path, State},
    http::StatusCode,
};
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

pub fn router() -> Router<AppState> {
    Router::new()
        .route("/course/{category}/{code}", get(get_course_by_pair))
        .merge(
            SwaggerUi::new("/swagger")
                .url("/openapi.json", crate::api::openapi::ApiDoc::openapi()),
        )
}

#[utoipa::path(
    get,
    path = "/course/{category}/{code}",
    tag = "course",
    responses(
        (status = 200, description = "Gets a course by its category and code", body = Course),
    ),
)]
async fn get_course_by_pair(
    State(AppState { db, .. }): State<AppState>,
    Path((category, code)): Path<(String, String)>,
) -> impl IntoResponse {
    match db::course::get_by_category_code(&db, &category, &code).await {
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
