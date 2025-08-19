use aide::axum::{ApiRouter, routing::get};
use nom::IResult;
use nom::Parser;
use nom::bytes::take_while_m_n;
use nom::combinator::all_consuming;
use nom::combinator::map;
use nom::sequence::pair;
use serde::{Deserialize, Serialize};

use crate::AppState;

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

pub fn router() -> ApiRouter<AppState> {
    ApiRouter::new().api_route("/test", get(raw::test))
}

fn is_alpha_ascii(c: char) -> bool {
    c.is_ascii_alphabetic()
}

fn parse_course_code(
    input: &str,
) -> IResult<&str, CourseCode> {
    map(
        all_consuming(pair(
            take_while_m_n(4, 4, is_alpha_ascii),
            take_while_m_n(4, 4, |c: char| {
                c.is_ascii_digit()
            }),
        )),
        |(prefix, postfix): (&str, &str)| CourseCode {
            prefix: prefix.to_string(),
            postfix: postfix.to_string(),
        },
    )
    .parse(input)
}
