from __future__ import annotations
from pprint import pprint
from serde import serde, AdjacentTagging
from serde.json import to_json, from_json


def main():
    print("HI THERE!")
    with open("../data/course_reqs/beme_reqs.json") as f:
        lines = f.read()
        out = from_json(Degree, lines)
        pprint(out)
        print(to_json(out))
        # print(out.programRequirements.keys())


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
    alternate: str | None
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
    payload: dict
    name: str
    type: str


@serde
class Payload:
    components: list[Component]


@serde
class ProgramRequirements:
    coPDF: dict
    code: str
    applicablePeriod: ApplicablePeriod
    publishInstanceID: int
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
    swaggerVersion: dict
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
