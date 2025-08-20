use anyhow::Context;
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, prelude::FromRow, query, query_as, query_scalar};
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
    // Option just to make inserting a bit nicer
    secat_id: Option<Uuid>,
    course_id: Uuid,
    num_enrolled: i32,
    num_responses: i32,
    response_rate: f32,
    questions: Option<Vec<SecatQuestion>>,
}

impl Secat {
    async fn load_by_course_id(db: &PgPool, course_id: Uuid) -> anyhow::Result<Option<Self>> {
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
        .await.context("Failed to get secat")
    }

    async fn store(&self, db: &PgPool) -> anyhow::Result<()> {
        let secat_id = query_scalar!(
            r#"
            INSERT INTO secats (course_id, num_enrolled, num_responses, response_rate)
            VALUES ($1,$2,$3,$4)
            RETURNING secats.secat_id
            "#,
            self.course_id,
            self.num_enrolled,
            self.num_responses,
            self.response_rate
        )
        .fetch_one(db)
        .await
        .context("Failed to insert secat into DB")?;

        let mut tx = db.begin().await?;
        if let Some(questions) = &self.questions {
            for secat_question in questions {
                query!(
                r#"
                    INSERT INTO secat_questions (secat_id, name, strongly_agree, agree, middle, disagree, strongly_disagree)
                    VALUES ($1,$2,$3,$4,$5,$6,$7)
                "#,
                secat_id,
                secat_question.name,
                secat_question.strongly_agree,
                secat_question.agree,
                secat_question.middle,
                secat_question.disagree,
                secat_question.strongly_disagree
            )
            .execute(&mut *tx)
            .await
            .context("")?;
            }
        }
        tx.commit().await?;

        Ok(())
    }
}
