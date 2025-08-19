//! Seeding: load courses from JSON and insert into DB (courses only).

use crate::db::course::{self, Course, CourseLevel, CourseMode, CourseSemester};
use anyhow::{Context, Result};
use serde::Deserialize;
use sqlx::PgPool;
use std::fs::File;
use std::io::BufReader;
use std::path::{Path, PathBuf};
use tracing::log::{info, warn};
use uuid::Uuid;

const DATA_DIR: &str = "data";
const COURSES_FILE: &str = "complete_courses.json";

#[derive(Debug, Deserialize)]
struct JsonCourse {
    // TODO this does not parse properly. It was just a quick copilot struct that was supposed to match the json but didnt. Will require actually thinking about the problem :(
    category: String,
    code: String,
    name: String,
    description: String,
    level: CourseLevel,
    num_units: i16,
    attendance_mode: CourseMode,
    #[serde(default = "default_active")]
    active: bool,
    semesters: Vec<CourseSemester>,
}

fn default_active() -> bool {
    true
}

/// Deals with the top-level JSON being either `{ "courses": [ ... ] }` or just `[ ... ]`.
#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum CourseContainer {
    Wrapped { courses: Vec<JsonCourse> },
    Flat(Vec<JsonCourse>),
}

impl CourseContainer {
    fn into_vec(self) -> Vec<JsonCourse> {
        match self {
            CourseContainer::Wrapped { courses } => courses,
            CourseContainer::Flat(v) => v,
        }
    }
}

/// Seeds the courses table.
///
/// - Skips rows that already exist by (category, code).
/// - Returns number of inserted rows.
pub async fn seed_courses(db: PgPool) -> Result<usize> {
    let path = Path::new(DATA_DIR).join(COURSES_FILE);
    info!(
        "Checking if course data needs seeding from {}",
        path.display()
    );

    let courses = load_courses_from_file(&path)
        .with_context(|| format!("failed to read courses JSON at {}", path.display()))?;

    if courses.is_empty() {
        info!("No courses found in JSON; nothing to seed.");
        return Ok(0);
    }

    let mut inserted = 0usize;

    for jc in courses {
        // Skip if (category, code) already exists.
        if let Some(_) = course::get_by_category_code(&db, &jc.category, &jc.code).await? {
            continue;
        }

        let model = Course {
            course_id: Uuid::new_v4(),
            category: jc.category,
            code: jc.code,
            name: jc.name,
            description: jc.description,
            level: jc.level,
            num_units: jc.num_units,
            attendance_mode: jc.attendance_mode,
            active: jc.active,
            semesters: jc.semesters,
        };

        match course::insert(&db, &model).await {
            Ok(_) => inserted += 1,
            Err(e) => {
                warn!(
                    "Failed to insert course {} {}: {e}",
                    model.category, model.code
                );
            }
        }
    }

    info!("Course seeding complete. Inserted {inserted} new courses.");
    Ok(inserted)
}

/// Loads courses from the JSON file.
fn load_courses_from_file(path: &Path) -> Result<Vec<JsonCourse>> {
    let file = File::open(path).with_context(|| format!("could not open {}", path.display()))?;
    let reader = BufReader::new(file);

    let container: CourseContainer =
        serde_json::from_reader(reader).with_context(|| "invalid course JSON")?;
    Ok(container.into_vec())
}
