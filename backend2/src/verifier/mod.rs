use aide::axum::{ApiRouter, routing::get};
use serde::{Deserialize, Serialize};

pub mod aux_rule;
pub mod raw;

pub type Units = u16;
pub type Level = u16;

/// Course code. Of the format CCCCNNNN.
/// where C is a alpha character, N is a digit.
#[derive(
    Debug, Clone, PartialEq, Eq, Serialize, Deserialize,
)]
pub struct CourseCode {
    pub prefix: String,
    pub postfix: String,
}

/// Program code. Of the format TODO.
#[derive(
    Debug, Clone, PartialEq, Eq, Serialize, Deserialize,
)]
pub struct ProgramCode {
    pub code: String,
}

/// Parts are complex identifiers into the tree of a courses rules.
/// Looks something like this:
/// Part      ::= Char Suffix*
/// Suffix    ::= "." ( Number | Char )
/// Number    ::= Digit+
#[derive(
    Debug, Clone, PartialEq, Eq, Serialize, Deserialize,
)]
pub struct PartLabel {
    symbols: Vec<PartSymbol>,
}

#[derive(
    Debug, Clone, PartialEq, Eq, Serialize, Deserialize,
)]
pub enum PartSymbol {
    Char(char),
    Num(i16),
}

pub fn router() -> ApiRouter {
    ApiRouter::new().api_route("/test", get(raw::test))
}
