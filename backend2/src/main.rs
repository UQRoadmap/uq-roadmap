#![allow(dead_code)]
mod api;
mod db;
mod scraping;
mod verifier;

use axum::Router;
use sqlx::PgPool;
use tracing::{debug, info};

#[derive(Clone, Debug)]
pub struct AppState {
    pub db: PgPool,
}

fn app() -> Router<AppState> {
    Router::new().merge(verifier::router()).merge(api::router())
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Enable logging:
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();
    info!("Server starting");

    let db = db::init().await?;
    let state = AppState { db };

    let app = app();

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();

    debug!("Listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app.with_state(state)).await?;

    Ok(())
}
