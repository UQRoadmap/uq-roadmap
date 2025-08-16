"use client"
import { useState, FormEvent, useEffect } from "react";

import { Field, FieldGroup, Fieldset, Label } from '@/components/fieldset'
import { Button } from '@/components/button'

import { Textarea } from "@/components/textarea";
import ValidateSection from "./validate";
const checks = [
  {
    "status": 2,
    "percentage": 0,
    "message": "0 units found in plan, but 8 required. Add from: ENGG1100",
    "relevant": [
      "ENGG1100"
    ]
  },
  {
    "status": 2,
    "percentage": null,
    "message": "No Field of Study found in plan. Add from: CHEMIX2350, CBIOMX2350, CBIOPX2350, CHENVX2350, CHMETX2350, CIVENX2350, CIENVX2350, ELENGX2350, ELEBEX2350, ELECEX2350, MECENX2350, MECAEX2350, MECMEX2350, MECTRX2350, SOFTEX2350",
    "relevant": [
      "CHEMIX2350",
      "CBIOMX2350",
      "CBIOPX2350",
      "CHENVX2350",
      "CHMETX2350",
      "CIVENX2350",
      "CIENVX2350",
      "ELENGX2350",
      "ELEBEX2350",
      "ELECEX2350",
      "MECENX2350",
      "MECAEX2350",
      "MECMEX2350",
      "MECTRX2350",
      "SOFTEX2350"
    ]
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 4 units from the following ['CHEM1090', 'PHYS1171', 'MATH1050']",
    "relevant": [
      "CHEM1090",
      "PHYS1171",
      "MATH1050"
    ]
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 4 units from the following ['BIOE1001', 'BIOL1040', 'CHEM1100', 'DSGN1500', 'ERTH1501', 'ENGG2000', 'PHYS1002']",
    "relevant": [
      "BIOE1001",
      "BIOL1040",
      "CHEM1100",
      "DSGN1500",
      "ERTH1501",
      "ENGG2000",
      "PHYS1002"
    ]
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 6 units from the following []",
    "relevant": []
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 6 units from the following []",
    "relevant": []
  }
]
import { DegreeSummary } from "../api/degrees/types";
import Dropdown from "./Dropdown";

export default function Home() {
  const [selectedDegree, setSelectedDegree] = useState<DegreeSummary | null>(null);
  const [startYear, setStartYear] = useState<number | null>(null);
  const [startSemester, setStartSemester] = useState<number>(1);
  const [planName, setPlanName] = useState<string>("");

  const [degreeSummaries, setDegreeSummaries] = useState<DegreeSummary[]>([])

  // Set default selections when degree changes
  useEffect(() => {
    async function fetchDegrees() {
      try {
        const res = await fetch("/api/degrees");
        if (!res.ok) throw new Error("Failed to fetch degrees");
        const data: DegreeSummary[] = await res.json();
        setDegreeSummaries(data);
      } catch (err) {
        console.error("Error fetching degrees:", err);
      }
    }
    fetchDegrees()
  }, []);

  // Set default selections when degree changes
  useEffect(() => {
    if (selectedDegree) {
      if (selectedDegree.years && selectedDegree.years.length > 0) {
        setStartYear(selectedDegree.years[0]);
      }
    }
  }, [selectedDegree]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    console.log("Form submitted. Selected degree:", selectedDegree);
    return;
    // if (selectedDegree) {
    //     const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";
    //     const id = v4();
    //     const offeringYear = parseInt(selectedOfferingYear || "0", 10);

    //     // Create the payload object to match the DegreeDBModel structure
    //     const payload = {
    //       id: id,
    //       degree_id: id,
    //       startYear: offeringYear,
    //       title: selectedDegree.name,
    //       json: {
    //         plan_id: id,
    //         degree_id: selectedDegree.id,
    //         degree: selectedDegree.name,
    //         planName: planName || `${selectedDegree.name} Plan` // Default name if none provided
    //       }
    //     };



    //     const result = await fetch(`${baseUrl}/plan/${id}`, {
    //         method: "POST",
    //         headers: { "Content-Type": "application/json" },
    //         body: JSON.stringify(payload),
    //     });

    //     if (result.status === 200) {
    //         const id = await result.json();
    //         router.push(`/plan/${id}`)
    //     }
    //     // need to handle validation error
    //     else {
    //         console.error("Unexpected error occurred, try again later")
    //     }
    // }
  };

  return (
    <div className="font-sans grid mt-2grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 max-w-7xl mx-auto px-4">
        <ValidateSection checks={checks} />
        <div className="font-sans flex flex-col items-center py-8 max-w-3xl mx-auto px-12">
        <form onSubmit={handleSubmit}>
        <Fieldset>
            <h1 className="text-3xl"> Start Your UQ Journey </h1>
            <FieldGroup>
                <Field>
                    <Label> Plan Name </Label>
                    <Textarea
                        resizable={false}
                        value={planName}
                        onChange={(e) => setPlanName(e.target.value)}
                        placeholder="Enter a name for your plan"
                    />
                </Field>
            <Dropdown
              label="Degree"
              options={degreeSummaries}
              value={selectedDegree ?? null}
              onChange={setSelectedDegree}
              displayValue={(d) => d?.title ?? ""}
              isEnabled
            />

            {(selectedDegree != null ?
                <Dropdown
                label="Start Year"
                options={selectedDegree?.years ?? []}
                value={startYear ?? (selectedDegree?.years?.[0] ?? null)}
                onChange={setStartYear}
                displayValue={(y) => y?.toString() ?? ""}
                id="start-year"
                isEnabled={!!selectedDegree}
                />
             : <></>)
            }

            {(startYear != null ?
                <Dropdown
                label="Start Semester"
                options={[1, 2]}
                value={startSemester}
                onChange={setStartSemester}
                displayValue={(v) => `Semester ${v}`}
                id="start-semester"
                isEnabled={!!startYear}
                />
             : <></>)
        }
            </FieldGroup>
            <Button type="submit" accent className="mt-5" disabled={!selectedDegree}> Add Courses </Button>
        </Fieldset>
        </form>
    </div>
  )
}
