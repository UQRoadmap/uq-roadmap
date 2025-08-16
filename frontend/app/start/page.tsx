"use client"
import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";

import { Field, FieldGroup, Fieldset, Label } from '@/components/fieldset'
import { Combobox, ComboboxLabel, ComboboxOption } from '@/components/combobox'
import { Button } from '@/components/button'

import MajorSelect from './major-comp'
import { v4 } from "uuid";
import { Textarea } from "@/components/textarea";

type Degree = { name: string; offerings: string[], id: string };

const degrees: Degree[] = [
    {
        name: "Bachelor of Software Engineering",
        id: "2",
        offerings: [
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "2026",
        ],
    },
    {
        name: "Bachelor of Computer Science",
        id: "1",
        offerings: [
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "2026",
        ],
    },
];

export default function Home() {
  const [selectedDegree, setSelectedDegree] = useState<Degree | null>(null);
  const [selectedMajor, setSelectedMajor] = useState<string | null>(null);
  const [selectedMinor, setSelectedMinor] = useState<string | null>(null);
  const [selectedOffering, setSelectedOffering] = useState<string | null>(null);
  const [graduationYear, setGraduationYear] = useState<string | null>(null);
  const [graduationSem, setGraduationSem] = useState<string | null>(null);
  const [planName, setPlanName] = useState<string>("");
  
  const router = useRouter();

  // Set default selections when degree changes
  useEffect(() => {
    if (selectedDegree) {
      // Set default value only for offering
      if (selectedDegree.offerings && selectedDegree.offerings.length > 0) {
        setSelectedOffering(selectedDegree.offerings[0]);
      }
      
      // Set major and minor to null by default
      setSelectedMajor(null);
      setSelectedMinor(null);
    }
  }, [selectedDegree]);

  // Set default graduation year and semester when offering is selected
    //   useEffect(() => {
    //     if (selectedOffering && selectedDegree) {
    //       const offerYear = parseInt(selectedOffering, 10);
    //       if (!Number.isNaN(offerYear)) {
    //         // Calculate the earliest graduation year based on units
    //         const earliestGradYear = offerYear + (selectedDegree.units > 0 ? Math.floor(selectedDegree.units / 16) : 0);
    //         setGraduationYear(String(earliestGradYear));
            
    //         // Set earliest graduation semester
    //         setGraduationSem("Semester 1");
    //       }
    //     }
    //   }, [selectedOffering, selectedDegree]);

  const semToNumber = (sem: string) => {
    if (sem !== "Summer Semester") {
        return sem.split(" ")[1]
    }
    else if (sem === "Summer Semester") return 3;
    else return "Unknown";
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    console.log("Form submitted. Selected degree:", selectedDegree);
    if (selectedDegree) {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";
        const id = v4();
        const offeringYear = parseInt(selectedOffering || "0", 10);
        
        // Create the payload object to match the DegreeDBModel structure
        const payload = {
          id: id,
          degree_id: id,
          startYear: offeringYear,
          title: selectedDegree.name,
          json: {
            plan_id: id,
            degree_id: selectedDegree.id,
            degree: selectedDegree.name,
            planName: planName || `${selectedDegree.name} Plan` // Default name if none provided
          }
        };
        
        
        // Store data in localStorage with plans_ prefix
        localStorage.setItem(`plans_${id}`, JSON.stringify(payload));
        
        const result = await fetch(`${baseUrl}/plan/${id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (result.status === 200) {
            const id = await result.json();
            router.push(`/plan/${id}`)
        }
        // need to handle validation error
        else {
            console.error("Unexpected error occurred, try again later")
        }
    }
  };

  return (
    <div className="font-sans grid mt-2grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 max-w-7xl mx-auto px-4">
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
                <Field>
                    <Label> Degree </Label>
                    <Combobox
                        name="degree"
                        options={degrees}
                        displayValue={(degree) => degree?.name}
                        aria-label="Your degree"
                        value={selectedDegree}
                        onChange={setSelectedDegree}
                    >
                        {degree => (
                            <ComboboxOption value={degree}>
                                <ComboboxLabel>{degree.name}</ComboboxLabel>
                            </ComboboxOption>
                        )}
                    </Combobox>
                </Field>
                <MajorSelect
                    name="Offerings"
                    options={selectedDegree?.offerings ?? []}
                    disabled={!selectedDegree}
                    setter={setSelectedOffering}
                />
            </FieldGroup>
            <Button type="submit" accent className="mt-5" disabled={!selectedDegree}> Add Courses </Button>
        </Fieldset>
        </form>
    </div>
  )
}