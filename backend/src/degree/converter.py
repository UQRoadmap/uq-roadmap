"""For converting parsed raw degree to nicer flat degree."""

from __future__ import annotations

import json
from pprint import pprint
from typing import Iterable, Optional, Tuple

from serde.json import from_dict, to_json

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
from degree.degree import Degree as FlatDegree
from degree.params import CourseRef, EquivalenceGroup, ProgramRef
from degree.sr_rule import (
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
from scraper.degree import (
    AuxiliaryRule as ParsedAuxRule,
)
from scraper.degree import (
    Component,
    ComponentPayload,
    ComponentPayloadHeader,
    CurriculumReference,
    WildCardItem,
    ComponentPayloadLeaf,
)
from scraper.degree import (
    Degree as ParsedDegree,
)
from scraper.degree import (
    EquivalenceGroup as ParsedEquivalenceGroup,
)
from scraper.degree import (
    Param as ParsedParam,
)
from scraper.degree import (
    SelectionRule as ParsedSelectionRule,
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

    # ...existing code...

    def _list_to_programs(v) -> list[ProgramRef]:
        if v is None:
            return []
        if isinstance(v, list):
            out: list[ProgramRef] = []
            for item in v:
                if isinstance(item, dict):
                    # Handle PLAN_WITH_PARENT structure in lists
                    if "plan" in item:
                        plan = item["plan"]
                        out.append(
                            ProgramRef(
                                units_max=plan.get("unitsMaximum"),
                                units_min=plan.get("unitsMinimum"),
                                code=plan.get("code", ""),
                                org_name=plan.get("orgName", ""),
                                org_code=plan.get("orgCode", ""),
                                name=plan.get("name", ""),
                                abbreviation=plan.get("abbreviation", ""),
                            )
                        )
                    else:
                        # Direct plan object
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
            return [_single_program(v)]  # Use _single_program for consistency
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

    # ...existing code...

    def _single_program(v) -> ProgramRef:
        if v is None:
            return ProgramRef(
                units_max=None, units_min=None, code="", org_name="", org_code="", name="", abbreviation=""
            )

        # Handle nested structure like {"parentProgram": {...}, "plan": {...}}
        if isinstance(v, dict):
            if "plan" in v:  # PLAN_WITH_PARENT structure
                plan = v["plan"]
                return ProgramRef(
                    units_max=plan.get("unitsMaximum"),
                    units_min=plan.get("unitsMinimum"),
                    code=plan.get("code", ""),
                    org_name=plan.get("orgName", ""),
                    org_code=plan.get("orgCode", ""),
                    name=plan.get("name", ""),
                    abbreviation=plan.get("abbreviation", ""),
                )
            else:  # Direct plan object
                return _to_program_ref(v)

        # Handle string (just a code)
        return ProgramRef(
            units_max=None, units_min=None, code=str(v), org_name="", org_code="", name="", abbreviation=""
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


def process_sr(parsed_sr: ParsedSelectionRule, rows: list[ComponentPayloadLeaf], part: str) -> SR:
    """Convert a parsed selection rule and its sibling leaves into a flat SR instance."""

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
        # Gather options from the sibling leaves of this SR node.
        courses: list[CourseRef] = []
        programs: list[ProgramRef] = []

        if not rows:
            return courses, programs

        for r in rows:
            # curriculumReference directly on the leaf?
            if r.curriculumReference is not None:
                cr = r.curriculumReference
                cr_d = cr if isinstance(cr, dict) else cr.__dict__
                t = cr_d.get("type")
                if t == "Course":
                    courses.append(_to_course_ref(cr_d))
                elif t in {"Program Rqt", "ProgramRqt", "Program"}:
                    programs.append(_to_program_ref(cr_d))

            # inside equivalenceGroup?
            if r.equivalenceGroup is not None:
                for eg in r.equivalenceGroup:
                    cr = eg.get("curriculumReference") if isinstance(eg, dict) else eg.curriculumReference
                    if cr is None:
                        continue
                    cr_d = cr if isinstance(cr, dict) else cr.__dict__
                    t = cr_d.get("type")
                    if t == "Course":
                        courses.append(_to_course_ref(cr_d))
                    elif t in {"Program Rqt", "ProgramRqt", "Program"}:
                        programs.append(_to_program_ref(cr_d))

        # de-dupe by code
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

    # gather options once (from the sibling leaves given to us)
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


# Replace the convert_degree function with this version that uses raw JSON:


def convert_degree(parsed_degree: ParsedDegree, raw_json: dict = None) -> FlatDegree:
    """Convert the recursive scraper.degree structure to a flat Degree.

    Also takes raw_json to extract course data when serde fails.
    """

    flat_degree = FlatDegree()
    flat_degree.name = parsed_degree.title
    flat_degree.code = parsed_degree.params.code
    flat_degree.year = parsed_degree.params.year

    # Collect here, then assign to flat_degree at the end.
    rule_logic_by_part: dict[str, str] = {}
    part_references: dict[str, str] = {}
    ars: list[AR] = []
    srs: list[SR] = []
    valid_parts: set[str] = set()

    # Fix the extract_courses_from_raw_json_for_part function:

    def extract_courses_from_raw_json_for_part(part: str) -> list[ComponentPayloadLeaf]:
        """Extract course data from raw JSON when serde fails."""
        if not raw_json:
            return []

        leaves = []

        def find_part_in_json(obj, target_part: str):
            if isinstance(obj, dict):
                # Check if this is a header with our target part
                if obj.get("header", {}).get("partReference") == target_part and "body" in obj:
                    for body_item in obj.get("body", []):
                        if body_item.get("rowType") == "CurriculumReference" and "curriculumReference" in body_item:
                            cr_data = body_item["curriculumReference"]

                            # Create a proper CurriculumReference object using the actual class
                            curriculum_ref = CurriculumReference(
                                unitsMaximum=cr_data.get("unitsMaximum"),
                                code=cr_data.get("code", ""),
                                orgName=cr_data.get("orgName", ""),
                                type=cr_data.get("type", "Course"),
                                version=cr_data.get("version"),
                                subtype=cr_data.get("subtype"),
                                fromYear=cr_data.get("fromYear"),
                                latestVersion=cr_data.get("latestVersion"),
                                unitsMinimum=cr_data.get("unitsMinimum"),
                                orgCode=cr_data.get("orgCode", ""),
                                name=cr_data.get("name", ""),
                                fromTerm=cr_data.get("fromTerm"),
                                state=cr_data.get("state"),
                            )

                            # Create ComponentPayloadLeaf manually
                            leaf = ComponentPayloadLeaf(
                                rowType=body_item.get("rowType"),
                                orderNumber=body_item.get("orderNumber"),
                                notes=body_item.get("notes"),
                                curriculumReference=curriculum_ref,
                                equivalenceGroup=None,
                                wildCardItem=None,
                            )

                            leaves.append(leaf)
                # Recurse through all values
                for value in obj.values():
                    find_part_in_json(value, target_part)
            elif isinstance(obj, list):
                for item in obj:
                    find_part_in_json(item, target_part)

        find_part_in_json(raw_json, part)
        return leaves

    def _walk(node: ComponentPayload, part_stack: list[str]) -> None:
        header = getattr(node, "header", None)
        # If this node declares a partReference, push it
        if header is not None:
            pr = header.partReference
            if pr:
                part_stack = [*part_stack, pr]
                valid_parts.add(pr)
                part_references[pr] = header.title or ""

            # Aux rules live on headers; attach only if we have a concrete part
            if header.auxiliaryRules:
                current_part = part_stack[-1] if part_stack else ""
                if current_part:
                    for ar in header.auxiliaryRules:
                        ars.append(process_ar(ar, current_part))

            # Rule logic for this part (if any)
            if pr and header.ruleLogic:
                rule_logic_by_part[pr] = header.ruleLogic

        # Split leaves vs child payloads
        sibling_leaves: list[ComponentPayloadLeaf] = []
        children_nodes: list[ComponentPayload] = []

        if getattr(node, "body", None) is not None:
            for child in node.body:
                if isinstance(child, ComponentPayloadLeaf):
                    sibling_leaves.append(child)
                else:
                    children_nodes.append(child)

        def collect_all_leaves(n: ComponentPayload) -> list[ComponentPayloadLeaf]:
            leaves = []

            if getattr(n, "body", None) is not None:
                for child in n.body:
                    if isinstance(child, ComponentPayloadLeaf):
                        leaves.append(child)
                    else:
                        # Recurse to find any properly deserialized leaves deeper
                        leaves.extend(collect_all_leaves(child))

            return leaves

        # Only attach SR when this very header declares a concrete part AND
        # the selectionRule has a valid code.
        if header is not None and header.partReference and header.selectionRule:
            sr_code = getattr(header.selectionRule, "code", None)
            if sr_code:  # skip empty selection rules
                current_part = header.partReference

                # First try serde-deserialized leaves
                all_leaves = collect_all_leaves(node)

                # If serde failed, extract from raw JSON
                if len(all_leaves) == 0:
                    all_leaves = extract_courses_from_raw_json_for_part(current_part)

                srs.append(process_sr(header.selectionRule, all_leaves, current_part))

        # Recurse
        for child_node in children_nodes:
            _walk(child_node, part_stack)

    # Only process the Program Requirements component with internalComponentIdentifier == 1
    for component in parsed_degree.programRequirements.payload.components:
        if component.internalComponentIdentifier != 1 or component.payload is None:
            continue
        _walk(component.payload, [])

    # Filter any AR/SR that somehow got a non-existent part
    ars = [a for a in ars if getattr(a, "part", "") in valid_parts]
    srs = [r for r in srs if getattr(r, "part", "") in valid_parts]

    # Assign outputs
    flat_degree.aux = ars
    flat_degree.srs = srs
    # Flatten rule logic to a unique list of strings
    flat_degree.rule_logic = list({v for v in rule_logic_by_part.values() if v})
    flat_degree.part_references = part_references
    return flat_degree


def main():
    with open("../data/program_details.json") as f:
        raw = f.read()
        details = json.loads(raw)["program_details"]

        for detail in details:
            for year, data in detail["data"].items():
                degree: ParsedDegree = from_dict(ParsedDegree | None, data)
                if degree is None:
                    continue

                # Pass the raw JSON data to the converter
                flat = convert_degree(degree, data)

                if len(flat.aux) > 10:
                    pprint(flat)
                    return

    # with open("../data/plans.json") as f:
    #     raw = f.read()
    #     raw_json = json.loads(raw)

    #     for plan in raw_json:
    #         plan_id = plan["plan_id"]
    #         data = plan["data"]
    #         for year, data in data.items():
    #             degree: ParsedDegree = from_dict(ParsedDegree | None, data)
    #             if degree is None:
    #                 continue

    #             # Pass the raw JSON data to the converter
    #             flat = convert_degree(degree, data)

    #             pprint(flat)
    #             return


# testing by printing to a file, it works
# import contextlib
# def main():
#     with open("../../data/course_reqs/details.json") as f:
#         raw = f.read()
#         details = json.loads(raw)["program_details"]

#         for detail in details:
#             for year, data in detail["data"].items():
#                 degree: ParsedDegree = from_dict(ParsedDegree | None, data)
#                 if degree is None:
#                     continue

#                 flat = convert_degree(degree, data)

#                 if len(flat.aux) > 10:
#                     # Redirect stdout to file (like freopen in C)
#                     with open("degree_output.txt", "w") as f:
#                         with contextlib.redirect_stdout(f):
#                             pprint(flat)
#                     print("Output written to degree_output.txt")
#                     return

if __name__ == "__main__":
    main()
