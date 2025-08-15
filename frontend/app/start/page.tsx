"use client"
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Description, Field, FieldGroup, Fieldset, Label, Legend } from '@/components/fieldset'
import { Combobox, ComboboxLabel, ComboboxOption } from '@/components/combobox'
import { Select } from '@/components/select'
import { Button } from '@/components/button'

import MajorSelect from './major-comp'

const degrees = [
    {
        name: "Bachelor of Software Engineering",
        majors: [
            "Design",
        ],
        minors: [
            "Data Science",
        ],
        offerings: [
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
        ],
    },
    {
        name: "Bachelor of Computer Science",
        majors: [
            "Design",
            "Programming Languages",
        ],
        offerings: [
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
        ],
    },
];

export default function Home() {
  const [selectedDegree, setSelectedDegree] = useState(null);
  const router = useRouter();

  const handleClick = () => {
    if (selectedDegree) {
      router.push("/courses"); // redirect to new page
    }
  };
  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
        <form action="/make_plan" method="POST" />
        {/* ... */}
        <Fieldset>
            <h1 className="text-3xl"> Start Your UQ Journey </h1>
            <FieldGroup>
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
                    options={selectedDegree?.offerings}
                    disabled={!selectedDegree}
                />
                <MajorSelect
                    name="Majors"
                    options={selectedDegree?.majors}
                    disabled={!selectedDegree || !selectedDegree.majors}
                />
                <MajorSelect
                    name="Minors"
                    options={selectedDegree?.minors}
                    disabled={!selectedDegree || !selectedDegree.minors}
                />
            </FieldGroup>
            <Button className="mt-5" disabled={!selectedDegree} onClick={handleClick}> Add Courses </Button>
        </Fieldset>
    </div>
  )
}
