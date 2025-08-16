from __future__ import annotations
from pprint import pprint
from serde import serde, AdjacentTagging
from serde.json import to_json, from_json
from serde import from_dict
import json


def main():
    with open("../data/course_reqs/details.json") as f:
        raw = f.read()
        details = json.loads(raw)["program_details"]
        components = {}
        rule_logic = set()
        ars = {}

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

                    rule_logic.add(component.payload.header.ruleLogic)

                    # program_rules[program_rule.header.ruleLogic] = program_rule.header.ruleLogic

        pprint(rule_logic)
        pprint(ars)


@serde
class AuxiliaryRule:
    code: str  # Seems like 1,2,6,7,9,10 are the only AR numbers
    text: str
    params: list[dict]


@serde
class ComponentPayloadHeader:
    title: str
    summaryDescription: str
    ruleLogic: str
    auxiliaryRules: list[AuxiliaryRule]


@serde
class ComponentPayloadBody:
    header: dict
    body: list[dict]


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
