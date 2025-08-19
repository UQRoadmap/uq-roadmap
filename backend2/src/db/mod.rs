//! Minimal sqlx setup: pool init, migrations, and helpers.

pub mod course;

use anyhow::Context;
use sqlx::{
    PgPool, Postgres, Transaction, postgres::PgPoolOptions,
};
use std::time::Duration;

/// Runs database migrations and returns a DbPool.
/// Call this once at startup! Don't re-run it.
/// If you want more pools just clone the pool it produces.
pub async fn init() -> anyhow::Result<PgPool> {
    let url = std::env::var("DATABASE_URL")
        .context("DATABASE_URL is not set")?;

    let pool =
        PgPoolOptions::new()
            .max_connections(env_u32("DB_MAX_CONNS", 10))
            .min_connections(env_u32("DB_MIN_CONNS", 1))
            .acquire_timeout(Duration::from_secs(env_u64(
                "DB_ACQUIRE_TIMEOUT_SECS",
                10,
            )))
            .idle_timeout(Some(Duration::from_secs(
                env_u64("DB_IDLE_TIMEOUT_SECS", 300),
            )))
            .max_lifetime(Some(Duration::from_secs(
                env_u64("DB_MAX_LIFETIME_SECS", 3600),
            )))
            .after_connect(|conn, _meta| {
                Box::pin(async move {
                    sqlx::query("SET TIME ZONE 'UTC'")
                        .execute(conn)
                        .await?;
                    Ok(())
                })
            })
            .connect(&url)
            .await?;

    // Run any db migrations
    sqlx::migrate!("./migrations").run(&pool).await?;

    Ok(pool)
}

fn env_u32(key: &str, default_: u32) -> u32 {
    std::env::var(key)
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(default_)
}

fn env_u64(key: &str, default_: u64) -> u64 {
    std::env::var(key)
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(default_)
}
