"use client";
import React, { useState, useEffect } from 'react';
import CourseCard, { EmptyCourseCard } from "@/components/custom/course-card";
import { ArrowDownIcon, ChevronDownIcon } from "@heroicons/react/20/solid";
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from '@/components/dropdown';
import Pop from '@/components/custom/palette'

import { MouseSensor, KeyboardSensor } from '@/components/custom-sensors'

import { DndContext, DragEndEvent, useSensor, useSensors  } from '@dnd-kit/core';
import { Course, DegreeReq } from '@/types/course';
import { v4 as uuidv4 } from "uuid";
import ProgressCircle from '@/components/custom/progressCircle';
import { Dialog, DialogBody, DialogTitle } from '@/components/dialog';
import { Textarea } from '@/components/textarea';
import { Button } from '@/components/button';
import { JacksonPlan, MapfromJacksonPlan } from '@/app/api/plan/types';


function SemesterSection({ semester, courses, setPaletteOpen, setActiveId, setDelete, courseReqs}:
    {
        semester: number; courses?: Course[], setPaletteOpen: (open: boolean) => void,
        setActiveId: (id: string) => void, setDelete: (id:string, sem:string) => void,
        courseReqs: DegreeReq
    }) {
    const [collapsed, setCollapsed] = useState(false);

    const normalCourses: Course[] = [];
    const overloadCourses: Course[] = [];
    let usedUnits = 0;

    if (courses && courses.length > 0) {
        courses.forEach((course) => {
            if (usedUnits + (course?.units ?? 0) <= 8) {
                normalCourses.push(course);
                usedUnits += course?.units ?? 0;
            } else {
                overloadCourses.push(course);
            }
        });
    }

    const getSemesterLabel = (sem: number) => {
        const year = Math.floor(sem / 10);
        const semesterNum = sem % 10;type DegreeReq = Record<string, string[]>;
        return `${year} Semester ${semesterNum}`;
    };

    const getColSpanClass = (units: number) => {
        switch (Math.floor(units)) {
            case 8:
                return 'col-span-8';
            case 4:
                return 'col-span-4';
            case 2:
                return 'col-span-2';
            case 1:
                return 'col-span-1';
            default:
                return 'col-span-1';
        }
    }

    return (
        <div key={semester} className="flex flex-col items-stretch justify-start gap-4 w-full p-4">
            <div
                className="flex justify-between items-center cursor-pointer"
            >
                <div>{getSemesterLabel(semester)}</div>
                <ChevronDownIcon
                    className={`w-5 h-5 transform transition-transform text-black hover:bg-gray-300 rounded-xl ${collapsed ? 'rotate-180' : ''}`}
                    onClick={() => setCollapsed(prev => !prev)}
                />
            </div>
            {!collapsed && (
                <>
                    <div className="grid grid-cols-8 w-full gap-2">
                        {Array.from({ length: 4 }).map((_, i) => {
                            const course = normalCourses.find(c => {
                                if (!c) return false;
                                const [_, pos] = c.sem.split("-"); // "20251-2"
                                return Number(pos) === i;
                            });

                            return (
                                <div
                                    key={`${course ? course.id : "empty"}-${semester}-${i}`}
                                    className={getColSpanClass(course ? course.units : 2)} // default empty to 2 units
                                >
                                    {course ?
                                        <CourseCard {...course} deleteMeth={setDelete} degreeReq={courseReqs}/>
                                        :
                                        <EmptyCourseCard id={`${semester}-${i}`} setPaletteOpen={setPaletteOpen} setActiveId={setActiveId} />
                                    }

                                </div>
                            );
                        })}
                    </div>

                    {overloadCourses.length > 0 && (
                        <div className="my-4 w-full rounded border-t-2 border-red-500 border-dotted">
                            <div className="space-y-2 mt-4">
                                <div className="flex items-center gap-1">
                                    <div>Overloaded Courses</div>
                                    <ArrowDownIcon className="h-3 ml-1" />
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export function PlanDetailClient({initialPlan, courses} : {initialPlan: JacksonPlan, courses: Course[]}) {
    const [plan, setPlan] = useState<JacksonPlan>(initialPlan);
    const [isPaletteOpen, setPaletteOpen] = useState(false);
    const [sem, setSem] = useState(undefined);
    const [isReversed, setIsReversed] = useState(false);

    const courseReqs: DegreeReq = {
        core: [
            "csse2310",
            "csse2010",
            "CSSE6400"
        ],
        electives: [
            "DATA2001",
            "CSSE6400"
        ],
    }

    const sensors = useSensors(
      useSensor(MouseSensor),
      useSensor(KeyboardSensor)
    );
    const [isPlanDialogOpen, setIsPlanDialogOpen] = useState(false);
    const [planDialogData, setPlanDialogData] = useState<string>("");

    function handleDragEnd(event: DragEndEvent) {
        const { active, over } = event;

        if (!over) return;

        const dragCourse = active.data.current as Course;
        if (!dragCourse) return;

        if (over.data?.current?.full) {
            // Two course cards to swap
            const targetCourseId = over.id.toString();

            setCourses((prevCourses) => {
                // Deep copy
                const newCourses = prevCourses.map((sem) => [...sem]);

                // Find both courses in the course array
                let dragSemIndex = -1;
                let dragCourseIndex = -1;
                let targetSemIndex = -1;
                let targetCourseIndex = -1;

                // Find the dragged course
                for (let i = 0; i < newCourses.length; i++) {
                    const courseIndex = newCourses[i].findIndex(c => c && c.id === dragCourse.id);
                    if (courseIndex !== -1) {
                        dragSemIndex = i;
                        dragCourseIndex = courseIndex;
                        break;
                    }
                }

                // Find the target course
                for (let i = 0; i < newCourses.length; i++) {
                    const courseIndex = newCourses[i].findIndex(c => c && c.id === targetCourseId);
                    if (courseIndex !== -1) {
                        targetSemIndex = i;
                        targetCourseIndex = courseIndex;
                        break;
                    }
                }

                // If both courses were found, swap them
                if (dragSemIndex !== -1 && targetSemIndex !== -1) {
                    const draggedCourse = { ...newCourses[dragSemIndex][dragCourseIndex] };
                    const targetCourse = { ...newCourses[targetSemIndex][targetCourseIndex] };

                    // Parse the semester values correctly
                    const [dragSemesterStr, dragPosStr] = draggedCourse.sem.split("-");
                    const [targetSemesterStr, targetPosStr] = targetCourse.sem.split("-");

                    // Create new sem values with swapped positions
                    draggedCourse.sem = `${targetSemesterStr}-${targetPosStr}`;
                    targetCourse.sem = `${dragSemesterStr}-${dragPosStr}`;

                    // Swap positions
                    newCourses[dragSemIndex][dragCourseIndex] = targetCourse;
                    newCourses[targetSemIndex][targetCourseIndex] = draggedCourse;

                    console.log("Swapped courses:", {
                        draggedFrom: `${dragSemIndex}-${dragCourseIndex}`,
                        draggedTo: `${targetSemIndex}-${targetCourseIndex}`,
                        draggedCourseSem: draggedCourse.sem,
                        targetCourseSem: targetCourse.sem
                    });
                }

                return newCourses;
            });

            setActiveId("");
            return;
        }

        const [targetSemIndexStr, targetIndexStr] = over.id.toString().split("-");

        const year = Math.floor(Number(targetSemIndexStr) / 10);
        const semNum = Number(targetSemIndexStr) % 10;

        let targetSemIndex;
        if (isReversed) {
            const totalSemesters = (plan.end_year - plan.start_year + 1) * 2
            targetSemIndex = totalSemesters - 1 - ((year - plan.start_year) * 2 + (semNum - 1));
        } else {
            targetSemIndex = (year - plan.start_year) * 2 + (semNum - 1);
        }

        const targetIndex = parseInt(targetIndexStr, 10);

        setCourses((prevCourses) => {
            // Deep copy
            const newCourses = prevCourses.map((sem) => [...sem]);

            // Check if course already exists in any semester
            const currentSemIndex = newCourses.findIndex((sem) => sem &&
                sem.some((c) => c.id === dragCourse.id)
            );

            // If it exists, remove from old semester
            if (currentSemIndex !== -1) {
                const courseIndex = newCourses[currentSemIndex].findIndex(
                    (c) => c && c.id === dragCourse.id
                );
                newCourses[currentSemIndex].splice(courseIndex, 1);
            }

            // Update semester property (optional)
            const updatedCourse = { ...dragCourse, sem: year.toString() + targetSemIndex.toString() + "-" + targetIndex };
            // Insert at target position
            newCourses[targetSemIndex].splice(targetIndex, 0, updatedCourse);
            console.log("drag", newCourses)
            return newCourses;
        });
        setActiveId("");
    }

    const handleInsertCourse = (course: Course, targetId: string) => {
        const [targetSemStr, targetIndexStr] = targetId.split("-");
        const year = Math.floor(Number(targetSemStr) / 10);
        const semNum = Number(targetSemStr) % 10;

        let targetSemIndex;
        if (isReversed) {
            const totalSemesters = (plan.end_year - plan.start_year + 1) * 2;
            targetSemIndex = totalSemesters - 1 - ((year - plan.start_year) * 2 + (semNum - 1));
        } else {
            targetSemIndex = (year - plan.start_year) * 2 + (semNum - 1);
        }

        const targetIndex = parseInt(targetIndexStr, 10);
        setCourses(prevCourses => {
            const newCourses = prevCourses.map(sem => [...sem]);

            const updatedCourse = { ...course, sem: targetId, id: uuidv4() };
            newCourses[targetSemIndex].splice(targetIndex, 0, updatedCourse); // replace empty card

            console.log("insert", newCourses)
            return newCourses;
        });
        setActiveId("");
    };

    function handleDeleteCourse(courseId: string, targetId: string) {
        const [targetSemStr] = targetId.split("-");
        const year = Math.floor(Number(targetSemStr) / 10);
        const semNum = Number(targetSemStr) % 10;

        let targetSemIndex;
        if (isReversed) {
            const totalSemesters = (plan.end_year - plan.start_year + 1) * 2;
            targetSemIndex = totalSemesters - 1 - ((year - plan.start_year) * 2 + (semNum - 1));
        } else {
            targetSemIndex = (year - plan.start_year) * 2 + (semNum - 1);
        }

        setCourses(prevCourses => {
            const newCourses = prevCourses.map(sem => [...sem]);

            // filter out the course by ID
            newCourses[targetSemIndex] = newCourses[targetSemIndex].filter(c => c.id !== courseId);

            console.log("delete", newCourses);
            return newCourses;
        });

        setActiveId("");
    };

    const [activeId, setActiveId] = useState<string>("");
    useEffect(() => {
        console.log("id change: ", activeId);
    });
    const [semesters, setSemesters] = useState<number[]>([]);
    const [stateCourses, setCourses] = useState<Course[][]>([]);

    useEffect(() => {
        if (plan) {
            const newSemesters: number[] = [];
            const newCourses: Course[][] = [];
            console.log(`START: ${plan.start_year}`)
            console.log(`END: ${plan.end_year}`)

            // Create the semester structure
            for (let year = plan.start_year; year <= plan.end_year; year++) {
                newSemesters.push(Number(`${year}1`));
                newSemesters.push(Number(`${year}2`));
                newCourses.push([]);
                newCourses.push([]);
            }

            // Populate courses from plan.course_tiles
            if (plan.course_tiles && Object.keys(plan.course_tiles).length > 0) {
                console.log("Loading courses from plan.course_tiles:", plan.course_tiles);

                Object.entries(plan.course_tiles).forEach(([key, courseCode]) => {
                    // Parse the key format: "20251-0" -> year=2025, sem=1, position=0
                    const [semesterPart, positionStr] = key.split("-");
                    const position = parseInt(positionStr, 10);

                    // Extract year and semester from semesterPart (e.g., "20251")
                    const year = Math.floor(parseInt(semesterPart, 10) / 10); // 2025
                    const semesterNum = parseInt(semesterPart, 10) % 10 + 1; // 1 -> 2, 0 -> 1

                    // Calculate the semester index in our array
                    const semesterIndex = (year - plan.start_year) * 2 + (semesterNum - 1);

                    // Find the course from the courses array
                    const course = courses.find(c => c.code === courseCode);

                    if (course && semesterIndex >= 0 && semesterIndex < newCourses.length) {
                        // Create a course instance with the correct sem property and unique ID
                        const courseInstance: Course = {
                            ...course,
                            id: uuidv4(), // Generate unique ID for this instance
                            sem: key // Keep the original key as sem property
                        };

                        // Insert the course at the correct position
                        // Ensure the array has enough slots
                        while (newCourses[semesterIndex].length <= position) {
                            newCourses[semesterIndex].push(null as any);
                        }
                        newCourses[semesterIndex][position] = courseInstance;

                        console.log(`Loaded course ${courseCode} at semester ${semesterIndex}, position ${position}`);
                    } else {
                        console.warn(`Could not load course: ${courseCode} (key: ${key})`);
                    }
                });

                // Remove null entries from arrays
                newCourses.forEach((semesterCourses, index) => {
                    newCourses[index] = semesterCourses.filter(course => course !== null);
                });
            }

            setSemesters(newSemesters);
            setCourses(newCourses);
            console.log("SEMESTERS", newSemesters);
            console.log("LOADED COURSES", newCourses);
        }
    }, [plan, courses]);

    useEffect(() => {
        if (stateCourses.length === 0 || stateCourses.flat().length == 0) {
            return;
        }
        if (plan) {
        console.log("Updating the state courses")
        console.log(JSON.stringify(stateCourses))
        let cur_sem = plan.start_sem;
        let cur_year = plan.start_year;
        let row_num = 0;
        let new_courses: Course[]
        let key: string;
        plan.course_tiles = {} // reset it
        while (row_num < stateCourses.length) {
            console.log(`Currently at ROW: ${row_num}`)
            console.log(`Currently at YEAR: ${cur_year}`)
            console.log(`Currently at SEM: ${cur_sem}`)
            new_courses = stateCourses[row_num]
            console.log(`There is ${new_courses.length} courses in this row`)
            for (let idx = 0; idx < new_courses.length; idx++) {
                key = `${cur_year}${cur_sem - 1}-${idx}`;
                console.log(`Setting ${key} -> ${new_courses[idx].code}`)
                plan.course_tiles[key] = new_courses[idx].code
            }
            console.log(`Course tiles is now: ${JSON.stringify(plan.course_tiles)}`)
            if (cur_sem == 2) {
                cur_sem = 1;
                cur_year += 1
            } else {
                cur_sem += 1
            }
            row_num += 1;
        }

        const body = MapfromJacksonPlan(plan, plan.degree.degree_id);
        async function set_value(){
            await fetch(`/api/plan/${plan.plan_id}`, {method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
            })
        }

        set_value();
    }

    }, [stateCourses])

    async function DeletePlan() {
        if (typeof window === "undefined" || !plan) return;
        const possibleKeys = [
            `plan-${plan.plan_id}`,
        ].filter(Boolean) as string[];

        possibleKeys.forEach((k) => {
            try {
                localStorage.removeItem(k);
            } catch (e) {
                console.warn("Failed to remove localStorage key", k, e);
            }
        });

        console.log("Deleted localStorage keys:", possibleKeys);
    }

    function sort() {
        setSemesters(prevSemesters => [...prevSemesters].reverse());
        setCourses(prevCourses => [...prevCourses].reverse());
        setIsReversed(prev => !prev);
    }

    // Function to open the dialog with plan data
    const openPlanDataDialog = () => {
        setPlanDialogData(JSON.stringify(plan, null, 2));
        setIsPlanDialogOpen(true);
    };

    // Function to save changes from the dialog
    const savePlanData = () => {
        try {
            const updatedPlan = JSON.parse(planDialogData);
            setPlan(updatedPlan);

            // Update localStorage
            if (plan && plan.plan_id) {
                localStorage.setItem(`plans_${plan.plan_id}`, planDialogData);
            }

            setIsPlanDialogOpen(false);
        } catch (e) {
            console.error(e)
            alert("Invalid JSON format. Please check your data.");
        }
    };

    return (
        <div>
            <div className="bg-secondary py-4 overflow-y-auto">
                <div className="max-w-7xl px-8 mx-auto flex items-center justify-between w-full">
                    {plan ? (
                        <>
                            <div>
                                <div className='flex items-center gap-x-6 gap-y-2'>
                                    <div className='text-white text-lg'>
                                        {plan.name}
                                    </div>
                                    <div className='ml-2'>
                                        <Dropdown>
                                            <DropdownButton accent>
                                                Options
                                                <ChevronDownIcon />
                                            </DropdownButton>
                                            <DropdownMenu>
                                                <DropdownItem onClick={() => openPlanDataDialog()}>Edit</DropdownItem>
                                                <DropdownItem className="hover:cursor-pointer" onClick={() => sort()}>Reverse Sorting</DropdownItem>
                                                <DropdownItem className="hover:cursor-pointer" onClick={async () => await DeletePlan()}>Delete</DropdownItem>
                                            </DropdownMenu>
                                        </Dropdown>
                                    </div>
                                </div>
                                <div className='my-4 text-xl text-white'>
                                    {plan.degree.title}
                                </div>
                                <div className='flex text-white italic'>
                                    <div>
                                        Planned Completion Date: {plan.end_year} Semester {plan.start_sem}
                                    </div>
                                </div>
                            </div>
                            <div className='flex flex-wrap items-center gap-x-6 gap-y-2'>
                                <ProgressCircle percentage={87} />
                            </div>
                        </>
                    ) : (
                        // This skeleton loader is likely not needed anymore since the page
                        // won't render until the plan is fetched, but keeping it just in case.
                        <>
                            <div className="flex-1">
                                <div className="flex items-center gap-x-6 gap-y-2">
                                    <div className="w-48 h-6 bg-gray-400/30 rounded-md animate-pulse" />
                                    <div className="ml-2">
                                        <div className="w-20 h-6 bg-gray-400/30 rounded-md animate-pulse" />
                                    </div>
                                </div>
                                <div className="my-4">
                                    <div className="w-128 h-5 bg-gray-400/30 rounded-md animate-pulse" />
                                </div>
                                <div className='flex text-white italic'>
                                    <div className="w-64 h-4 bg-gray-400/30 rounded-md animate-pulse" />
                                </div>
                            </div>
                            <div className='flex flex-wrap items-center gap-x-6 gap-y-2'>
                                <div className="w-24 h-24 rounded-full bg-gray-400/30 animate-pulse" />
                            </div>
                        </>
                    )}
                </div>
            </div>
            <div className='max-w-7xl mx-auto px-4'>
                <DndContext
                    sensors={sensors}
                    onDragStart={({ active }) => setActiveId(active.id as string)}
                    onDragEnd={handleDragEnd}
                >
                    <Pop
                        clickable
                        setActiveId={setActiveId}
                        activeId={activeId}
                        opened={isPaletteOpen}
                        setPaletteOpen={setPaletteOpen}
                        onSelectCourse={handleInsertCourse}
                        sem={sem}
                        stateCourses={stateCourses}
                        setDelete={handleDeleteCourse}
                        courseReqs={courseReqs}
                        courses={courses}
                    />

                    <div className="flex flex-col h-screen overflow-y-auto">
                        {semesters.map((semester, i) => (
                            <SemesterSection
                                key={semester}
                                semester={semester}
                                courses={stateCourses[i]}
                                setPaletteOpen={setPaletteOpen}
                                setActiveId={setActiveId}
                                setDelete={handleDeleteCourse}
                                courseReqs={courseReqs}
                            />
                        ))}
                    </div>
                </DndContext>
            </div>


            {/* Dialog for Plan Data */}
            <Dialog
                open={isPlanDialogOpen}
                onClose={(open: boolean) => {
                    setIsPlanDialogOpen(open);
                    if (!open) {
                        // reset edits when dialog is closed without saving
                        setPlanDialogData(plan ? JSON.stringify(plan, null, 2) : "");
                    }
                }}
            >
                <DialogTitle>Plan Data</DialogTitle>
                <div className="text-sm text-gray-600 mt-2">
                    Edit the raw plan JSON. Saving will overwrite the current plan and update localStorage.
                </div>
                <DialogBody className="sm:max-w-4xl bg-white shadow-lg border border-gray-200 opacity-100 mt-4">
                    <div className="mt-2">
                        <Textarea
                            value={planDialogData}
                            onChange={(e) => setPlanDialogData((e.target as HTMLTextAreaElement).value)}
                            className="font-mono text-sm h-96 w-full"
                        />
                    </div>
                    <div className="mt-4 flex justify-end gap-2">
                        <Button
                            onClick={() => {
                                setIsPlanDialogOpen(false);
                                setPlanDialogData(plan ? JSON.stringify(plan, null, 2) : "");
                            }}
                            className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={savePlanData}
                            className="px-4 py-2 text-white rounded"
                            accent
                        >
                            Save Changes
                        </Button>
                    </div>
                </DialogBody>
            </Dialog>
        </div>
    );
}
