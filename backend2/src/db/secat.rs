use serde::{Deserialize, Serialize};
use sqlx::{PgPool, prelude::FromRow, query_as};
use utoipa::ToSchema;
use uuid::Uuid;

#[derive(Serialize, Deserialize, Debug, FromRow, Clone, ToSchema)]
pub struct SecatQuestion {
    question_id: Uuid,
    secat_id: Uuid,
    name: String,
    strongly_agree: f32,
    agree: f32,
    middle: f32,
    disagree: f32,
    strongly_disagree: f32,
}

#[derive(Serialize, Deserialize, Debug, FromRow, Clone, ToSchema)]
pub struct Secat {
    secat_id: Uuid,
    course_id: Uuid,
    num_enrolled: i32,
    num_responses: i32,
    response_rate: f32,
    questions: Vec<SecatQuestion>,
}

impl SecatQuestion {
    async fn load(db: &PgPool) -> Self {
        todo!()
    }

    async fn store(self, db: &PgPool) {
        todo!()
    }
}

impl Secat {
    async fn load_by_course_id(db: &PgPool, course_id: Uuid) -> Self {
        // secat_id      uuid PRIMARY KEY,
        // course_id     uuid REFERENCES courses(course_id),
        // num_enrolled  bigint NOT NULL,
        // num_responses bigint NOT NULL,
        // response_rate real NOT NULL
        query_as!(
            Secat,
            r#"
            SELECT
              secat_id, course_id, num_enrolled, num_responses,
              response_rate
            FROM secats
            WHERE course_id = $1
            "#,
            course_id
        )
        .fetch_optional(db)
        .await
    }

    async fn store(&self, db: &PgPool) {
        todo!()
    }
}
