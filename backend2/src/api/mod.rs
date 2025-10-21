mod course;
mod openapi;

use crate::AppState;
use axum::Router;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

pub fn router() -> Router<AppState> {
    Router::new().nest("/course", course::router()).merge(
        SwaggerUi::new("/swagger").url("/openapi.json", crate::api::openapi::ApiDoc::openapi()),
    )
}
