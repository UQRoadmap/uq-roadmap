//! The raw program requirements representation.
//! Deserialized from json directly via serde.

use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Params {}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Status {}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ProgramRequirements {}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Degree {
    pub title: String,
    pub params: Params,
    pub status: Status,
    pub program_requirements: ProgramRequirements,
    pub year_options: Vec<String>,
    pub routes: HashMap<String, Value>,
}
