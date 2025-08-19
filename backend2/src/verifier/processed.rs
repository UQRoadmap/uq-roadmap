use anyhow::bail;
use nom::AsChar;
use nom::IResult;
use nom::Parser;
use nom::bytes::take_while_m_n;
use nom::combinator::all_consuming;
use nom::combinator::map;
use nom::sequence::pair;
use std::{
    ops::{Range, RangeInclusive},
    str::FromStr,
};

use nom::bytes::{take_while, take_while1};

#[derive(Debug, Clone, PartialEq, Eq)]
struct CourseCode {
    prefix: String,
    postfix: String,
}

struct ProgramCode {
    code: String,
}

fn is_alpha_ascii(c: char) -> bool {
    c.is_ascii_alphabetic()
}

fn parse_course_code(input: &str) -> IResult<&str, CourseCode> {
    map(
        all_consuming(pair(
            take_while_m_n(4, 4, is_alpha_ascii),
            take_while_m_n(4, 4, |c: char| c.is_ascii_digit()),
        )),
        |(prefix, postfix): (&str, &str)| CourseCode {
            prefix: prefix.to_string(),
            postfix: postfix.to_string(),
        },
    )
    .parse(input)
}

pub enum AuxiliaryRule {
    Ar1 {
        n: i64,
        level: i64,
        or_higher: bool,
    },
    Ar2 {
        n: i64,
        level: i64,
    },
    Ar3 {
        n: i64,
        level: i64,
        or_higher: bool,
    },
    Ar4 {
        n: i64,
        m: i64,
        level: i64,
        or_higher: bool,
    },
    Ar5 {
        plan_list_1: Vec<ProgramCode>,
        plan_list_2: Vec<ProgramCode>,
    },
    Ar6 {
        plan_list_1: Vec<ProgramCode>,
        plan_list_2: Vec<ProgramCode>,
    },
}
