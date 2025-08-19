//! Auxiliary rules definitions.

use nom::IResult;
use nom::Parser;
use nom::bytes::take_while_m_n;
use nom::combinator::all_consuming;
use nom::combinator::map;
use nom::sequence::pair;
use serde::Deserialize;
use serde::Serialize;

use crate::verifier::CourseCode;
use crate::verifier::Level;
use crate::verifier::PartLabel;
use crate::verifier::ProgramCode;
use crate::verifier::Units;

#[derive(
    Debug, Clone, PartialEq, Eq, Serialize, Deserialize,
)]
pub struct LevelSpec {
    pub level: Level,
    pub or_higher: bool,
}

pub struct AuxiliaryRule {
    part: PartLabel,
    rule: AuxiliaryRuleKind,
}

#[derive(
    Debug, Clone, PartialEq, Eq, Serialize, Deserialize,
)]
#[serde(tag = "type")]
pub enum AuxiliaryRuleKind {
    /// At least [N] units at level [LEVEL][OR_HIGHER]
    #[serde(rename = "AR1")]
    Ar1 {
        n: Units,
        #[serde(flatten)]
        spec: LevelSpec,
    },

    /// At most [N] units at level [LEVEL]
    #[serde(rename = "AR2")]
    Ar2 { n: Units, level: Level },

    /// Exactly [N] units at level [LEVEL][OR_HIGHER]
    #[serde(rename = "AR3")]
    Ar3 {
        n: Units,
        #[serde(flatten)]
        spec: LevelSpec,
    },

    /// [N] to [M] units at level [LEVEL][OR_HIGHER]
    #[serde(rename = "AR4")]
    Ar4 {
        n: Units,
        m: Units,
        #[serde(flatten)]
        spec: LevelSpec,
    },

    /// [PLAN_LIST_1] only with [PLAN_LIST_2].
    #[serde(rename = "AR5")]
    Ar5 {
        plan_list_1: Vec<ProgramCode>,
        plan_list_2: Vec<ProgramCode>,
    },

    /// [PLAN_LIST_1] NOT with [PLAN_LIST_2].
    #[serde(rename = "AR6")]
    Ar6 {
        plan_list_1: Vec<ProgramCode>,
        plan_list_2: Vec<ProgramCode>,
    },

    /// No more than [N] units from same discipline descriptor.
    Ar7 { n: Units },

    /// No credit for [COURSE_LIST].
    #[serde(rename = "AR9")]
    Ar9 { course_list: Vec<CourseCode> },

    /// No credit for [COURSE_LIST] for students completing [PLAN_LIST].
    #[serde(rename = "AR10")]
    Ar10 {
        course_list: Vec<CourseCode>,
        plan_list: Vec<ProgramCode>,
    },

    /// No credit for [COURSE_LIST] unless completing [PLAN_LIST].
    #[serde(rename = "AR11")]
    Ar11 {
        course_list: Vec<CourseCode>,
        plan_list: Vec<ProgramCode>,
    },

    /// Students undertaking [PLAN_LIST] are exempt from [COURSE_LIST] in [PROGRAM_PLAN_LIST].
    #[serde(rename = "AR13")]
    Ar13 {
        plan_list: Vec<ProgramCode>,
        course_list: Vec<CourseCode>,
        program_plan_list: Vec<ProgramCode>,
    },

    /// [COURSE_LIST] [MUST/MAY] be substituted in [PROGRAM_PLAN_LIST] by a course from [LISTS].
    #[serde(rename = "AR15")]
    Ar15 {
        course_list: Vec<CourseCode>,
        must: bool,
        program_plan_list: Vec<ProgramCode>,
        lists: Vec<String>,
    },

    /// For students in [PLAN_LIST] - [COURSE_LIST_1] [MUST/MAY] be substituted by [COURSE_LIST_2] in [PROGRAM_PLAN_LIST].
    #[serde(rename = "AR16")]
    Ar16 {
        plan_list: Vec<ProgramCode>,
        course_list_1: Vec<CourseCode>,
        must: bool,
        course_list_2: Vec<CourseCode>,
        program_plan_list: Vec<ProgramCode>,
    },

    /// For students in [PLAN_LIST] - [COURSE_LIST] [MUST/MAY] be substituted by a course from [LISTS] in [PROGRAM_PLAN_LIST].
    #[serde(rename = "AR17")]
    Ar17 {
        plan_list: Vec<ProgramCode>,
        course_list: Vec<CourseCode>,
        must: bool,
        program_plan_list: Vec<ProgramCode>,
        lists: Vec<String>,
    },

    /// [COURSE_LIST] can only be counted towards the [PROGRAM] component of a dual.
    #[serde(rename = "AR18")]
    Ar18 {
        course_list: Vec<CourseCode>,
        program: ProgramCode,
    },

    /// For students completing [PLAN_LIST], [COURSE_LIST] only counts towards [PROGRAM] component.
    #[serde(rename = "AR19")]
    Ar19 {
        plan_list: Vec<ProgramCode>,
        course_list: Vec<CourseCode>,
        program: ProgramCode,
    },

    /// For students completing [PLAN] and [PLAN_LIST_1], [COURSE_LIST] only counts towards [PLAN_LIST_2].
    #[serde(rename = "AR20")]
    Ar20 {
        plan_1: ProgramCode,
        plan_list_1: Vec<ProgramCode>,
        course_list: Vec<CourseCode>,
        plan_list_2: Vec<ProgramCode>,
    },

    /// Fallback to preserve anything unexpected (future-proof).
    #[serde(rename = "ARUnknown")]
    ArUnknown {
        text: String,
        raw_params: Vec<serde_json::Value>,
    },
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
