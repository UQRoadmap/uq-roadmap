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
        // query_as!(
        //     Course,
        //     r#"
        //     SELECT
        //       course_id, category, code, name, description,
        //       level as "level: _",
        //       num_units,
        //       attendance_mode as "attendance_mode: _",
        //       active,
        //       semesters as "semesters: _"
        //     FROM courses
        //     WHERE category = $1 AND code = $2
        //     "#,
        //     category,
        //     code
        // )
        // .fetch_optional(db)
        // .await
        todo!()
    }

    async fn store(&self, db: &PgPool) {
        todo!()
    }
}
