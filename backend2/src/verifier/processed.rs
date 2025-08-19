use anyhow::bail;
use nom::AsChar;
use nom::IResult;
use nom::Parser;
use std::{
    ops::{Range, RangeInclusive},
    str::FromStr,
};

use nom::bytes::{take_while, take_while1};

pub struct ProgramCode {
    prefix: String,
    postfix: String,
}

impl FromStr for ProgramCode {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let IResult::Ok((rem, (a, b))) = (
            take_while1(AsChar::is_alpha),
            take_while1(AsChar::is_dec_digit),
        )
            .parse(s)
        else {
            bail!("NO");
        };

        Ok(ProgramCode {
            prefix: a.to_owned(),
            postfix: b.to_owned(),
        })
    }
}

pub struct Program {
    units: Option<RangeInclusive<i64>>,
    code: ProgramCode,
    org_name: String,
    org_code: String,
    name: String,
    abbreviation: String,
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
