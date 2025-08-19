use serde::{Deserialize, Serialize};
use sqlx::{PgPool, prelude::FromRow, query_as};
use utoipa::ToSchema;
use uuid::Uuid;

#[derive(Serialize, Deserialize, Debug, FromRow, Clone, ToSchema, sqlx::Type)]
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
    questions: Option<Vec<SecatQuestion>>,
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
        query_as!(
            Secat,
            r#"
            SELECT
                s.secat_id,
                s.course_id,
                s.num_enrolled,
                s.num_responses,
                s.response_rate,
                COALESCE(ARRAY_AGG((q.question_id, q.secat_id, q.name, q.strongly_agree, q.agree, q.middle, q.disagree, q.strongly_disagree)), '{}') AS "questions: Vec<SecatQuestion>"
            FROM secats as s
            LEFT JOIN LATERAL (
                SELECT
                    q.question_id,
                    q.secat_id,
                    q.name,
                    q.strongly_agree,
                    q.agree,
                    q.middle,
                    q.disagree,
                    q.strongly_disagree
                FROM secat_questions AS q
                WHERE q.secat_id = s.secat_id
                ORDER BY q.question_id
            ) AS q ON TRUE
            WHERE course_id = $1
            GROUP BY s.secat_id, s.course_id, s.num_enrolled, s.num_responses, s.response_rate
            "#,
            course_id
        )
        .fetch_optional(db)
        .await.unwrap().unwrap()
    }

    async fn store(&self, db: &PgPool) {
        todo!()
    }
}
