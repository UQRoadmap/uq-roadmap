"use client"
import { useState, useEffect } from "react";

import { Field, FieldGroup, Fieldset, Label } from '@/components/fieldset'
import { Button } from '@/components/button'

import { Textarea } from "@/components/textarea";
import { APIDegreeRead, DegreeSummary } from "../api/degree/types";
import BetterDropdown from "../../components/custom/Dropdown";
import { APIPlanCreateUpdate, JacksonPlan, LucasReadPlan } from "../api/plan/types";
import { useRouter } from "next/navigation";

function buildArrayFrom(num: number, len: number = 8) {
    return Array.from({ length: len }, (_, i) => num + i + 1);
}

export default function Home() {
    const router = useRouter();

    const [selectedDegree, setSelectedDegree] = useState<DegreeSummary | null>(null);
    const [startYear, setStartYear] = useState<number | null>(null);
    const [endYear, setEndYear] = useState<number | null>(null);
    const [startSemester, setStartSemester] = useState<1 | 2>(1);
    const [planName, setPlanName] = useState<string>("");

    const [degreeSummaries, setDegreeSummaries] = useState<DegreeSummary[]>([])


    useEffect(() => {
        async function fetchDegrees() {
            try {
                const res = await fetch("/api/degree/summary");
                if (!res.ok) {
                    console.error(await res.text())
                    throw new Error("Failed to fetch degrees");
                }
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

    const [loading, setLoading] = useState<boolean>(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        setLoading(true);
        console.log(loading);
        e.preventDefault();
        console.log("Form submitted. Selected degree:", selectedDegree);
        if (!selectedDegree) {
            return;
        }

        if (!startYear || !endYear) {
            console.warn("Form submitted but start year is null or end year is null...")
            return;
        }

        const res = await fetch(`/api/degree?degree_code=${selectedDegree.degree_code}&year=${startYear}`)
        if (res.status == 404) {
            console.error("Degree not found", await res.text());
            return
        }
        if (!res.ok) {
            console.error("Unexpected error:", await res.text());
            return;
        }

        const degree: APIDegreeRead = await res.json();

        const createPayload: APIPlanCreateUpdate = {
            name: planName,
            degree_id: degree.degree_id,
            start_year: startYear,
            end_year: endYear,
            start_sem: startSemester,
            course_dates_input: {},
            course_reqs: {},
            specialisations: {}
        }

        try {
            console.log(createPayload)
            const res = await fetch("/api/plan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(createPayload),
            });

            if (res.status === 404) {
                alert("Selected degree could not be found for this year.");
                return;
            }

            if (!res.ok) {
                const errorText = await res.text();
                alert(`Failed to create plan: ${errorText}`);
                return;
            }

            const newPlan: JacksonPlan = await res.json();

            console.log("Plan created successfully:", newPlan);
            router.push(`/plan/${newPlan.plan_id}`);
        } catch (err) {
            console.error(err);
            alert("An unexpected error occurred. Please try again.");
        }

    };

    return (
        <div className="font-sans grid mt-2grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 max-w-7xl mx-auto px-4">
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
                            <BetterDropdown
                                label="Degree"
                                options={degreeSummaries}
                                value={selectedDegree ?? null}
                                onChange={setSelectedDegree}
                                displayValue={(d) => d?.title ?? ""}
                                isEnabled
                            />

                            {(selectedDegree != null ?
                                <BetterDropdown
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
                                <BetterDropdown
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

                            {(startYear != null ?
                                <BetterDropdown
                                    label="End Year"
                                    options={buildArrayFrom(startYear, 8)}
                                    value={endYear}
                                    onChange={setEndYear}
                                    displayValue={(v) => v?.toString() ?? ""}
                                    id="end-year"
                                    isEnabled={!!startYear}
                                />
                                : <></>)}
                        </FieldGroup>
                        <div className="flex justify-center mt-5">
                            {loading ? (
                                <Button type="submit" accent disabled className="flex items-center justify-center">
                                    <span
                                        className="inline-block h-5 w-5 mr-1 animate-spin rounded-full border-2 border-white border-t-transparent"
                                        role="status"
                                        aria-hidden="true"
                                    />
                                    Creating...
                                </Button>
                            ) : (
                                <Button type="submit" accent disabled={!selectedDegree}>
                                    Create Plan
                                </Button>
                            )}
                        </div>
                    </Fieldset>
                </form>
            </div>
        </div>
    )
}
