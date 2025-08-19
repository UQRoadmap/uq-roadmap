use axum::{
    Json, Router,
    http::StatusCode,
    response::{Html, IntoResponse},
    routing::get,
};
use serde::{Deserialize, Serialize};
use tracing::{debug, info};

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
    Router::new().route("/", get(test))
}

#[derive(Serialize, Deserialize)]
struct Response {
    magic: String,
}

async fn test() -> impl IntoResponse {
    let response = Response {
        magic: "Hello".to_string(),
    };
    (StatusCode::OK, Json(response))
}
