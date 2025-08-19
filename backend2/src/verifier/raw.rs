use std::collections::HashMap;

use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct Params {}

#[derive(Deserialize, Serialize)]
pub struct Status {}

#[derive(Deserialize, Serialize)]
pub struct ProgramRequirements {}

#[derive(Deserialize, Serialize)]
pub struct Degree {
    title: String,
    params: Params,
    status: Status,
    program_requirements: ProgramRequirements,
    year_options: Vec<String>,
    routes: HashMap<String, String>,
}
