mod verifier;

use aide::{
    IntoApi,
    axum::{
        ApiRouter, IntoApiResponse,
        routing::{get, post},
    },
    openapi::{Info, OpenApi},
    swagger::Swagger,
};
use axum::{
    Extension, Json, ServiceExt,
    http::StatusCode,
    response::{Html, IntoResponse},
};
use schemars::JsonSchema;
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

    let mut api = OpenApi {
        info: Info {
            description: Some("an example API".to_string()),
            ..Info::default()
        },
        ..OpenApi::default()
    };

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();

    debug!("Listening on {}", listener.local_addr().unwrap());
    axum::serve(
        listener,
        app.finish_api(&mut api)
            .layer(Extension(api))
            .into_make_service(),
    )
    .await
    .unwrap();
}

async fn serve_api(Extension(api): Extension<OpenApi>) -> impl IntoResponse {
    Json::<OpenApi>(api)
}

fn app() -> ApiRouter {
    ApiRouter::new()
        .api_route("/", get(test))
        .route("/api.json", axum::routing::get(serve_api))
        .route("/swagger", Swagger::new("/api.json").axum_route())
}

#[derive(Serialize, Deserialize, JsonSchema)]
struct Response {
    magic: String,
}

async fn test() -> impl IntoApiResponse {
    let response = Response {
        magic: "Hello".to_string(),
    };
    (StatusCode::OK, Json(response))
}
