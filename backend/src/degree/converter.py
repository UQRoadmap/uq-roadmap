"""For converting parsed raw degree to nicer flat degree."""

from __future__ import annotations

from typing import Iterable, Optional, Tuple

from serde.json import from_dict, to_json
from pprint import pprint
import json

from scraper.degree import (
    Degree as ParsedDegree,
    Component,
    ComponentPayload,
    ComponentPayloadHeader,
    ComponentPayloadBody,
    ComponentPayloadBodyHeader,
    ComponentPayloadBodyBody,
    ComponentPayloadBodyBodyHeader,
    ComponentPayloadBodyBodyBody,
    SelectionRule as ParsedSelectionRule,
    AuxiliaryRule as ParsedAuxRule,
    CurriculumReference,
    WildCardItem,
    EquivalenceGroup as ParsedEquivalenceGroup,
    Param as ParsedParam,
)

from degree.degree import Degree as FlatDegree
from degree.params import CourseRef, ProgramRef, EquivalenceGroup
from degree.aux_rule import (
    AR,
    AR1,
    AR2,
    AR3,
    AR4,
    AR5,
    AR6,
    AR7,
    AR9,
    AR10,
    AR11,
    AR13,
    AR15,
    AR16,
    AR17,
    AR18,
    AR19,
    AR20,
    ARUnknown,
)
from degree.srs_rule import (
    SR,
    SR1,
    SR2,
    SR3,
    SR4,
    SR5,
    SR6,
    SR7,
    SR8,
)


def process_ar(parsed_ar: ParsedAuxRule, part: str) -> AR:
    """Convert a parsed auxiliary rule into a flat AR instance."""

    # Helpers
    def _num(x) -> int:
        if isinstance(x, int):
            return x
        if isinstance(x, str) and x.isdigit():
            return int(x)
        # be tolerant of accidental numeric strings like "2 " or "02"
        try:
            return int(str(x).strip())
        except Exception:
            return 0

    def _bool(x, default: bool = True) -> bool:
        if isinstance(x, bool):
            return x
        if x is None:
            return default
        s = str(x).strip().lower()
        if s in {"true", "t", "yes", "y", "1", "must"}:
            return True
        if s in {"false", "f", "no", "n", "0", "may"}:
            return False
        return default

    def _to_course_ref(d: dict) -> CourseRef:
        ver = d.get("version") or {}
        units_max = d.get("unitsMaximum")
        units_min = d.get("unitsMinimum")
        return CourseRef(
            units_max=d.get("unitsMaximum"),
            units_min=d.get("unitsMinimum"),
            code=d.get("code") or "",
            org_name=d.get("orgName") or "",
            org_code=d.get("orgCode") or "",
            name=d.get("name") or "",
        )

    def _to_program_ref(d: dict) -> ProgramRef:
        ver = d.get("version") or {}
        return ProgramRef(
            units_max=d.get("unitsMaximum"),
            units_min=d.get("unitsMinimum"),
            code=d.get("code") or "",
            org_name=d.get("orgName") or "",
            org_code=d.get("orgCode") or "",
            name=d.get("name") or "",
            abbreviation=d.get("abbreviation") or "",
        )

    def _list_to_courses(v) -> list[CourseRef]:
        if v is None:
            return []
        if isinstance(v, list):
            # either list[dict] (CurriculumReference) or list[str] (codes)
            out: list[CourseRef] = []
            for item in v:
                if isinstance(item, dict):
                    out.append(_to_course_ref(item))
                else:
                    # minimal fallback when only a code string is present
                    out.append(
                        CourseRef(
                            units_max=None,
                            units_min=None,
                            code=str(item),
                            org_name="",
                            org_code="",
                            name="",
                        )
                    )
            return out
        if isinstance(v, dict):
            return [_to_course_ref(v)]
        # single code string
        return [
            CourseRef(
                units_max=None,
                units_min=None,
                code=str(v),
                org_name="",
                org_code="",
                name="",
            )
        ]

    def _list_to_programs(v) -> list[ProgramRef]:
        if v is None:
            return []
        if isinstance(v, list):
            out: list[ProgramRef] = []
            for item in v:
                if isinstance(item, dict):
                    out.append(_to_program_ref(item))
                else:
                    out.append(
                        ProgramRef(
                            units_max=None,
                            units_min=None,
                            code=str(item),
                            org_name="",
                            org_code="",
                            name="",
                            abbreviation="",
                        )
                    )
            return out
        if isinstance(v, dict):
            return [_to_program_ref(v)]
        return [
            ProgramRef(
                units_max=None,
                units_min=None,
                code=str(v),
                org_name="",
                org_code="",
                name="",
                abbreviation="",
            )
        ]

    def _single_program(v) -> ProgramRef:
        ps = _list_to_programs(v)
        return (
            ps[0]
            if ps
            else ProgramRef(
                units_max=None,
                units_min=None,
                code="",
                org_name="",
                org_code="",
                name="",
                abbreviation="",
            )
        )

    # index params by name for convenience
    params = {p.name: p for p in (parsed_ar.params or [])}
    get = lambda key, default=None: (params.get(key).value if key in params else default)

    code = parsed_ar.code

    # Level/units style rules
    if code == "AR1":
        return AR1(
            part=part,  # part is set by the caller's context
            n=_num(get("N", 0)),
            level=_num(get("LEVEL", 0)),
            or_higher=_bool(get("OR_HIGHER", True), True),
        )
    if code == "AR2":
        return AR2(
            part=part,
            n=_num(get("N", 0)),
            level=_num(get("LEVEL", 0)),
        )
    if code == "AR3":
        return AR3(
            part=part,
            n=_num(get("N", 0)),
            level=_num(get("LEVEL", 0)),
            or_higher=_bool(get("OR_HIGHER", True), True),
        )
    if code == "AR4":
        return AR4(
            part=part,
            n=_num(get("N", 0)),
            m=_num(get("M", 0)),
            level=_num(get("LEVEL", 0)),
            or_higher=_bool(get("OR_HIGHER", True), True),
        )

    # Plan compatibility rules
    if code == "AR5":
        return AR5(
            part=part,
            plan_list_1=_list_to_programs(get("PLAN_LIST_1", [])),
            plan_list_2=_list_to_programs(get("PLAN_LIST_2", [])),
        )
    if code == "AR6":
        return AR6(
            part=part,
            plan_list_1=_list_to_programs(get("PLAN_LIST_1", [])),
            plan_list_2=_list_to_programs(get("PLAN_LIST_2", [])),
        )

    # Discipline cap
    if code == "AR7":
        return AR7(part=part, n=_num(get("N", 0)))

    # Credit restrictions
    if code == "AR9":
        return AR9(part=part, course_list=_list_to_courses(get("COURSE_LIST", [])))
    if code == "AR10":
        return AR10(
            part=part,
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            plan_list=_list_to_programs(get("PLAN_LIST", [])),
        )
    if code == "AR11":
        return AR11(
            part=part,
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            plan_list=_list_to_programs(get("PLAN_LIST", [])),
        )

    # Exemptions / substitutions
    if code == "AR13":
        return AR13(
            part=part,
            plan_list=_list_to_programs(get("PLAN_LIST", [])),
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            program_plan_list=_list_to_programs(get("PROGRAM_PLAN_LIST", [])),
        )
    if code == "AR15":
        # MUST/MAY may arrive as boolean or string
        must = _bool(get("MUST", get("MUST_OR_MAY", True)), True)
        # LISTS is a list of strings (ids/names of lists)
        lists_val = get("LISTS", [])
        lists: list[str] = []
        if isinstance(lists_val, list):
            for x in lists_val:
                lists.append(str(x))
        elif lists_val is not None:
            lists = [str(lists_val)]
        return AR15(
            part=part,
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            must=must,
            program_plan_list=_list_to_programs(get("PROGRAM_PLAN_LIST", [])),
            lists=lists,
        )
    if code == "AR16":
        must = _bool(get("MUST", get("MUST_OR_MAY", True)), True)
        return AR16(
            part=part,
            plan_list=_list_to_programs(get("PLAN_LIST", [])),
            course_list_1=_list_to_courses(get("COURSE_LIST_1", [])),
            must=must,
            course_list_2=_list_to_courses(get("COURSE_LIST_2", [])),
            program_plan_list=_list_to_programs(get("PROGRAM_PLAN_LIST", [])),
        )
    if code == "AR17":
        must = _bool(get("MUST", get("MUST_OR_MAY", True)), True)
        # LISTS again expected as list[str]
        lists_val = get("LISTS", [])
        lists: list[str] = []
        if isinstance(lists_val, list):
            lists = [str(x) for x in lists_val]
        elif lists_val is not None:
            lists = [str(lists_val)]
        return AR17(
            part=part,
            plan_list=_list_to_programs(get("PLAN_LIST", [])),
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            must=must,
            program_plan_list=_list_to_programs(get("PROGRAM_PLAN_LIST", [])),
            lists=lists,
        )

    # Dual attribution constraints
    if code == "AR18":
        return AR18(
            part=part,
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            program=_single_program(get("PROGRAM")),
        )
    if code == "AR19":
        return AR19(
            part=part,
            plan_list=_list_to_programs(get("PLAN_LIST", [])),
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            program=_single_program(get("PROGRAM")),
        )
    if code == "AR20":
        return AR20(
            part=part,
            plan_1=_single_program(get("PLAN")),
            plan_list_1=_list_to_programs(get("PLAN_LIST_1", [])),
            course_list=_list_to_courses(get("COURSE_LIST", [])),
            plan_list_2=_list_to_programs(get("PLAN_LIST_2", [])),
        )

    # Fallback so we don't lose future/unknown rules
    raw_params = []
    for p in parsed_ar.params or []:
        raw_params.append({"name": p.name, "type": p.type, "value": p.value})
    return ARUnknown(part=part, text=getattr(parsed_ar, "text", ""), raw_params=raw_params)


def process_sr(parsed_sr: ParsedSelectionRule, rows: list[ComponentPayloadBodyBodyBody], part: str) -> SR:
    def _num(x) -> int:
        if isinstance(x, int):
            return x
        if isinstance(x, str) and x.isdigit():
            return int(x)
        try:
            return int(str(x).strip())
        except Exception:
            return 0

    def _to_course_ref(d: dict) -> CourseRef:
        return CourseRef(
            units_max=d.get("unitsMaximum"),
            units_min=d.get("unitsMinimum"),
            code=d.get("code") or "",
            org_name=d.get("orgName") or "",
            org_code=d.get("orgCode") or "",
            name=d.get("name") or "",
        )

    def _to_program_ref(d: dict) -> ProgramRef:
        return ProgramRef(
            units_max=d.get("unitsMaximum"),
            units_min=d.get("unitsMinimum"),
            code=d.get("code") or "",
            org_name=d.get("orgName") or "",
            org_code=d.get("orgCode") or "",
            name=d.get("name") or "",
            abbreviation=d.get("abbreviation") or "",
        )

    def _collect_options() -> tuple[list[CourseRef], list[ProgramRef]]:
        courses: list[CourseRef] = []
        programs: list[ProgramRef] = []

        if not rows:
            return courses, programs

        for r in rows:
            if r.curriculumReference is not None:
                cr = r.curriculumReference
                if (cr.type or cr.type) == "Course":
                    courses.append(_to_course_ref(cr if isinstance(cr, dict) else cr.__dict__))
                elif (cr.type or cr.type) in {"Program Rqt", "ProgramRqt", "Program"}:
                    programs.append(_to_program_ref(cr if isinstance(cr, dict) else cr.__dict__))

            if r.equivalenceGroup is not None:
                eq_list = r.equivalenceGroup
                for eg in eq_list:
                    cr = eg.get("curriculumReference") if isinstance(eg, dict) else eg.curriculumReference
                    if cr is None:
                        continue
                    if (cr.type if isinstance(cr, dict) else cr.type) == "Course":
                        courses.append(_to_course_ref(cr if isinstance(cr, dict) else cr.__dict__))
                    elif (cr.type if isinstance(cr, dict) else cr.type) in {
                        "Program Rqt",
                        "ProgramRqt",
                        "Program",
                    }:
                        programs.append(_to_program_ref(cr if isinstance(cr, dict) else cr.__dict__))

        seen_c: set[str] = set()
        dedup_courses: list[CourseRef] = []
        for c in courses:
            if c.code not in seen_c:
                seen_c.add(c.code)
                dedup_courses.append(c)

        seen_p: set[str] = set()
        dedup_programs: list[ProgramRef] = []
        for p in programs:
            if p.code not in seen_p:
                seen_p.add(p.code)
                dedup_programs.append(p)

        return dedup_courses, dedup_programs

    # index params by name for convenience
    params = {p.name: p for p in (parsed_sr.params or [])}
    get = lambda key, default=None: (params.get(key).value if key in params else default)

    # gather options once
    course_opts, program_opts = _collect_options()

    code = parsed_sr.code

    # ---- SR mappings --------------------------------------------------------
    if code == "SR1":  # Complete [N] units for ALL of the following
        return SR1(part=part, n=_num(get("N", 0)), options=course_opts)

    if code == "SR2":  # Complete [N] to [M] units for ALL of the following
        return SR2(part=part, n=_num(get("N", 0)), m=_num(get("M", 0)), options=course_opts)

    if code == "SR3":  # Complete at least [N] units from the following
        return SR3(part=part, n=_num(get("N", 0)), options=course_opts)

    if code == "SR4":  # Complete [N] to [M] units from the following
        return SR4(part=part, n=_num(get("N", 0)), m=_num(get("M", 0)), options=course_opts)

    if code == "SR5":  # Complete exactly [N] units from the following
        return SR5(part=part, n=_num(get("N", 0)), options=course_opts)

    if code == "SR6":  # Complete one [PLANTYPE] from the following
        # sometimes it's PLANTYPE, sometimes PLANTYPE_SINGULAR
        plan_type = get("PLANTYPE", get("PLANTYPE_SINGULAR", ""))
        plan_type = "" if plan_type is None else str(plan_type)
        return SR6(part=part, plan_type=plan_type, options=program_opts)

    if code == "SR7":  # Complete exactly [N] [PLANTYPES] from the following
        plan_types = get("PLANTYPES", "")
        plan_types = "" if plan_types is None else str(plan_types)
        return SR7(part=part, n=_num(get("N", 0)), plan_types=plan_types, options=program_opts)

    if code == "SR8":  # Complete [N] to [M] [PLANTYPES] from the following
        plan_types = get("PLANTYPES", "")
        plan_types = "" if plan_types is None else str(plan_types)
        return SR8(part=part, n=_num(get("N", 0)), m=_num(get("M", 0)), plan_types=plan_types, options=program_opts)

    # unknown future SR type: keep part so it still validates as a no-op SR
    return SR(part=part)


def convert_degree(parsed_degree: ParsedDegree) -> FlatDegree:
    flat_degree = FlatDegree()
    flat_degree.name = parsed_degree.title
    flat_degree.code = parsed_degree.params.code
    flat_degree.year = parsed_degree.params.year

    # Get all of the auxiliaries from the parsed degree.
    # Making sure they have the right part id.

    # Same for SRS.
    rule_logic = {}
    ars = []
    ar_params = set()
    row_types = set()
    srs = []
    sr_params: dict[str, set] = {}
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
    letter = 0

    for component in parsed_degree.programRequirements.payload.components:
        if component.internalComponentIdentifier != 1:
            continue

        # Initial aux rules are going to have no part, ""
        part = ""
        for ar in component.payload.header.auxiliaryRules:
            ars.append(process_ar(ar, part))

        rule_logic[part] = component.payload.header.ruleLogic

        for body in component.payload.body:
            # print(body)
            # These are all still root nodes
            # Very sad!
            part = body.header.partReference
            # print(part)
            for ar in body.header.auxiliaryRules:
                ars.append(process_ar(ar, part))

            for body2 in body.body:
                print("----")
                print(part)
                if body2.header is None:
                    continue

                print(">>")
                part = body2.header.partReference
                print(part)

                if body2.header.auxiliaryRules is not None:
                    for ar in body2.header.auxiliaryRules:
                        ars.append(process_ar(ar, part))

                if body2.header.selectionRule is None or body2.body is None:
                    continue

                sr = body2.header.selectionRule

                rows = []
                for body3 in body2.body:
                    # Course references and program references are here.
                    # We dont really care about tracking these tooooo much except that the selection rule should probably store them in their lists.
                    rows.append(body3)

                # to process SR we need the SR and its body (ikr!)
                srs.append(process_sr(sr, rows, part))
                # print(part)
                # print(srs[-1])

    # pprint(ars)

    flat_degree.aux = ars
    flat_degree.srs = srs

    # rule logic...? hmmmm

    return flat_degree


def main():
    with open("../../data/course_reqs/details.json") as f:
        raw = f.read()
        details = json.loads(raw)["program_details"]
        components = {}
        rule_logic = set()
        ars = {}
        ar_params = set()
        row_types = set()
        srs = {}
        sr_params: dict[str, set] = {}

        for detail in details:
            for year, data in detail["data"].items():
                degree: ParsedDegree = from_dict(ParsedDegree | None, data)
                if degree is None:
                    continue

                print("--------------------------------")
                print("--------------------------------")
                print("--------------------------------")
                print("--------------------------------")
                flat = convert_degree(degree)

                with open("../../data/magic.json", "w") as f2:
                    f2.write(to_json(degree))

                if len(flat.aux) > 10:
                    pprint(flat)
                    return


if __name__ == "__main__":
    main()
