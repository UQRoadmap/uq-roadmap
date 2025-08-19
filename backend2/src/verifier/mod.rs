use aide::axum::{ApiRouter, routing::get};
use axum::http::StatusCode;

pub mod processed;
pub mod raw;

pub fn router() -> ApiRouter {
    ApiRouter::new().api_route("/test", get(raw::test))
}
