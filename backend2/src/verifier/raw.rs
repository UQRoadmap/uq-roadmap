//! The raw program requirements representation.
//! Deserialized from json directly via serde.

use axum::{Json, http::StatusCode, response::IntoResponse};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{collections::HashMap, fs::File, io::Read, path::Path};
use tracing::info;
use utoipa::ToSchema;

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Param {
    pub name: String,
    #[serde(rename = "type")]
    pub r#type: String,
    pub value: Option<ParamValue>,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(untagged)]
pub enum ParamValue {
    Int(i64),
    Str(String),
    Obj(HashMap<String, Value>),
    Arr(Vec<HashMap<String, Value>>),
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct AuxiliaryRule {
    pub code: String,
    pub text: String,
    pub params: Vec<Param>,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct SelectionRule {
    pub code: String,
    pub text: String,
    pub params: Vec<Param>,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct ComponentPayloadHeader {
    #[serde(rename = "partUID")]
    pub part_uid: Option<String>,
    pub rule_logic: Option<String>,
    pub part_reference: Option<String>,
    pub units_min: Option<i64>,
    pub auxiliary_rules: Vec<AuxiliaryRule>,
    pub title: String,
    pub summary_description: Option<String>,
    pub part_type: Option<String>,
    pub units_max: Option<i64>,
    pub notes: Option<String>,
    pub selection_rule: Option<SelectionRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct CurriculumReference {
    pub units_maximum: Option<i64>,
    pub code: Option<String>,
    pub org_name: String,
    #[serde(rename = "type")]
    pub r#type: String,
    pub version: Value,
    pub subtype: Option<String>,
    pub from_year: Option<String>,
    pub latest_version: Option<bool>,
    pub units_minimum: Option<i64>,
    pub org_code: String,
    pub name: String,
    pub from_term: Option<String>,
    pub state: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct WildCardItem {
    pub code: String,
    pub org_name: Option<String>,
    pub org_code: Option<String>,
    pub include_child_orgs: bool,
    #[serde(rename = "type")]
    pub r#type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct EquivalenceGroup {
    pub order_number: i64,
    pub notes: Option<String>,
    pub curriculum_reference: CurriculumReference,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase", tag = "rowType")]
pub enum ComponentPayloadLeaf {
    #[serde(rename = "curriculumReference", alias = "CurriculumReference")]
    CurriculumReference {
        order_number: Option<i64>,
        notes: Option<String>,
        curriculum_reference: CurriculumReference,
    },

    #[serde(rename = "equivalenceGroup", alias = "EquivalenceGroup")]
    EquivalenceGroup {
        order_number: Option<i64>,
        notes: Option<String>,
        equivalence_group: Vec<EquivalenceGroup>,
    },

    #[serde(rename = "wildCardItem", alias = "WildCardItem")]
    WildCardItem {
        order_number: Option<i64>,
        notes: Option<String>,
        wild_card_item: WildCardItem,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct ComponentPayloadNode {
    pub header: Option<ComponentPayloadHeader>,
    pub body: Option<Vec<ComponentPayload>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(untagged)]
pub enum ComponentPayload {
    Node(ComponentPayloadNode),
    Leaf(ComponentPayloadLeaf),
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Params {
    #[serde(rename = "type")]
    pub r#type: String,
    pub code: String,
    pub year: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Domestic {
    pub suspension: bool,
    pub available: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Status {
    pub no_longer_offered: bool,
    pub alternate: Option<HashMap<String, Value>>,
    pub domestic: Domestic,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct International {
    pub suspension: bool,
    pub available: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct ApplicablePeriod {
    pub to_year: Option<String>,
    pub to_term: Option<String>,
    pub from_year: String,
    pub from_term: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Component {
    pub internal_component_identifier: i64,
    pub component_integration_identifier: String,
    pub payload: ComponentPayload,
    pub name: String,
    #[serde(rename = "type")]
    pub r#type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Payload {
    pub components: Vec<Component>,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct ProgramRequirements {
    #[serde(rename = "coPDF")]
    pub co_pdf: Value,
    pub code: String,
    pub applicable_period: Option<ApplicablePeriod>,
    #[serde(rename = "publishInstanceID")]
    pub publish_instance_id: Option<i64>,
    #[serde(rename = "type")]
    pub r#type: String,
    pub org_parent: String,
    pub author_last_name: String,
    pub subtype: String,
    pub payload: Payload,
    pub org_code: String,
    pub external_system_identifiers: Vec<Value>,
    pub state: String,
    pub units_maximum: Option<i64>,
    pub org_name: String,
    pub base_version: Value,
    pub workflow_name: String,
    pub version: Value,
    pub edit_date: String,
    pub previous_state: String,
    pub swagger_version: Option<Value>,
    pub template_name: String,
    pub units_minimum: Option<i64>,
    pub template_integration_identifier: String,
    pub year_applied: String,
    pub author_given_name: String,
    pub name: String,
    pub template_version: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Degree {
    pub title: String,
    pub params: Params,
    pub status: Status,
    pub program_requirements: ProgramRequirements,
    pub year_options: Vec<String>,
    pub routes: HashMap<String, Value>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ProgramDetail {
    pub program_id: String,
    pub data: HashMap<String, Option<Degree>>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ProgramDetails {
    program_details: Vec<ProgramDetail>,
}

pub async fn test() -> impl IntoResponse {
    let path = Path::new("../backend/data/program_details.json");
    let mut file = File::open(path).unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    let degree: ProgramDetails = serde_json::from_str(&contents).unwrap();
    info!(degree=?degree.program_details[0]);

    (StatusCode::OK, Json(degree.program_details[0].clone()))
}
