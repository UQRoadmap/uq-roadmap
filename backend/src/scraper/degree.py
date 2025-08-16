from __future__ import annotations
from pprint import pprint
from serde import serde, AdjacentTagging
from serde.json import to_json, from_json
from serde import from_dict
from json import loads


def main():
    with open("../data/course_reqs/details.json") as f:
        raw = f.read()
        details = loads(raw)["program_details"]
        components = {}
        rule_logic = set()
        ars = {}
        ar_params = set()
        row_types = set()
        srs = {}
        sr_params: dict[str, set] = {}

        for detail in details:
            for year, data in detail["data"].items():
                degree: Degree = from_dict(Degree | None, data)
                if degree is None:
                    continue

                for component in degree.programRequirements.payload.components:
                    components[component.internalComponentIdentifier] = component.type
                    if component.internalComponentIdentifier != 1:
                        continue

                    for ar in component.payload.header.auxiliaryRules:
                        ars[ar.code] = ar.text
                        for param in ar.params:
                            ar_params.add(param.type)

                    rule_logic.add(component.payload.header.ruleLogic)

                    for body in component.payload.body:
                        for ar in body.header.auxiliaryRules:
                            ars[ar.code] = ar.text
                            for param in ar.params:
                                ar_params.add(param.type)

                        for body2 in body.body:
                            if body2.header is not None and body2.header.auxiliaryRules is not None:
                                for ar in body2.header.auxiliaryRules:
                                    ars[ar.code] = ar.text
                                    for param in ar.params:
                                        ar_params.add(param.type)

                            if body2.header is not None and body2.header.selectionRule is not None:
                                srs[body2.header.selectionRule.code] = body2.header.selectionRule.text
                                for param in body2.header.selectionRule.params:
                                    if param.name not in sr_params:
                                        sr_params[param.name] = set()
                                    sr_params[param.name].add(param.type)

                            if body2.body is not None:
                                for body3 in body2.body:
                                    row_types.add(body3.rowType)
                                    if body3.rowType == "CurriculumReference":
                                        row_types.add((body3.rowType, body3.curriculumReference.type))

        pprint(rule_logic)
        pprint(ars)
        pprint(srs)
        pprint(row_types)
        pprint(ar_params)
        pprint(sr_params)


@serde
class Param:
    name: str
    type: str
    value: int | dict | list[dict] | str | None


@serde
class AuxiliaryRule:
    code: str  # Seems like 1,2,6,7,9,10 are the only AR numbers
    text: str
    params: list[Param]


@serde
class ComponentPayloadHeader:
    title: str
    summaryDescription: str
    ruleLogic: str
    auxiliaryRules: list[AuxiliaryRule]


@serde
class ComponentPayloadBodyHeader:
    partUID: str | None
    ruleLogic: str | None
    partReference: str
    unitsMin: int | None
    auxiliaryRules: list[AuxiliaryRule]
    title: str
    summaryDescription: str | None
    partType: str
    unitsMax: int | None
    notes: str | None
    selectionRule: SelectionRule | None
    partType: str


@serde
class SelectionRule:
    code: str
    text: str
    params: list[Param]


@serde
class ComponentPayloadBodyBodyHeader:
    partUID: str | None
    notes: str | None
    partReference: str
    auxiliaryRules: list[AuxiliaryRule] | None
    selectionRule: SelectionRule | None
    title: str
    partType: str


@serde
class CurriculumReference:
    unitsMaximum: int
    code: str | None
    orgName: strmponentPayloadBod
    type: str
    version: dict
    subtype: str | None
    fromYear: str | None
    latestVersion: bool | None
    unitsMinimum: int
    orgCode: str
    name: str
    fromTerm: str | None
    state: str


@serde
class WildCardItem:
    code: str
    orgName: str | None
    orgCode: str | None
    includeChildOrgs: bool
    type: str


@serde
class EquivalenceGroup:
    orderNumber: int
    notes: str | None
    curriculumReference: CurriculumReference


@serde
class ComponentPayloadBodyBodyBody:
    rowType: str | None
    orderNumber: int | None
    notes: str | None
    # PYSERDE SUCKS COMPARED TO SERDE!!!
    curriculumReference: CurriculumReference | None
    equivalenceGroup: list[EquivalenceGroup] | None
    wildCardItem: WildCardItem | None


@serde
class ComponentPayloadBodyBody:
    header: ComponentPayloadBodyBodyHeader | None
    body: list[ComponentPayloadBodyBodyBody] | None


@serde
class ComponentPayloadBody:
    header: ComponentPayloadBodyHeader
    body: list[ComponentPayloadBody]


@serde
class ComponentPayload:
    header: ComponentPayloadHeader | None
    body: list[ComponentPayloadBody] | None


@serde
class Params:
    type: str
    code: str
    year: str


@serde
class Domestic:
    suspension: bool
    available: bool


@serde
class Status:
    noLongerOffered: bool
    alternate: dict | None
    domestic: Domestic


@serde
class International:
    suspension: bool
    available: bool


@serde
class ApplicablePeriod:
    toYear: str | None
    toTerm: str | None
    fromYear: str
    fromTerm: str


@serde
# @serde(tagging=AdjacentTagging("internalComponentIdentifier", "payload"))
class Component:
    internalComponentIdentifier: int
    componentIntegrationIdentifier: str
    payload: ComponentPayload
    name: str
    type: str


@serde
class Payload:
    components: list[Component]


@serde
class ProgramRequirements:
    coPDF: dict
    code: str
    applicablePeriod: ApplicablePeriod | None
    publishInstanceID: int | None
    type: str
    orgParent: str
    authorLastName: str
    subtype: str
    payload: Payload
    orgCode: str
    externalSystemIdentifiers: list
    state: str
    unitsMaximum: int
    orgName: str
    baseVersion: dict
    workflowName: str
    version: dict
    editDate: str
    previousState: str
    swaggerVersion: dict | None
    templateName: str
    unitsMinimum: int
    templateIntegrationIdentifier: str
    yearApplied: str
    authorGivenName: str
    name: str
    templateVersion: int


@serde
class Degree:
    title: str
    params: Params
    status: Status
    programRequirements: ProgramRequirements
    yearOptions: list[str]
    routes: dict


if __name__ == "__main__":
    main()
