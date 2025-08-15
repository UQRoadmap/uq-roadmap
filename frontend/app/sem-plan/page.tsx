"use client";
import React, { useState } from 'react';
import CourseCard, { EmptyCourseCard } from "@/components/custom/course-card";
import { ArrowDownIcon, ChevronDownIcon } from "@heroicons/react/20/solid";

type CourseInfo = { name: string; id: string; units: number; degreeReq: string; sem: number; completed: boolean };

function SemesterSection({ semester, courses }: { semester: number; courses: CourseInfo[] }) {
    const [collapsed, setCollapsed] = useState(false);
    let usedUnits = 0;
    const normalCourses: CourseInfo[] = [];
    const overloadCourses: CourseInfo[] = [];
    courses.forEach(course => {
        if (usedUnits + course.units <= 8) {
            normalCourses.push(course);
            usedUnits += course.units;
        } else {
            overloadCourses.push(course);
        }
    });
    const emptySlots = Math.floor((8 - usedUnits) / 2);


    const getSemesterLabel = (sem: number) => {
        const year = Math.floor(sem / 10);
        const semesterNum = sem % 10;
        return `${year} Semester ${semesterNum}`;
    };

    const getColSpanClass = (units: number) => {
        switch (units) {
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
                    className={`w-5 h-5 transform transition-transform text-black hover:bg-gray-800 rounded-xl ${collapsed ? 'rotate-180' : ''}`}
                    onClick={() => setCollapsed(prev => !prev)}
                />
            </div>
            {!collapsed && (
                <>
                    <div className="grid grid-cols-8 w-full gap-2">
                        {normalCourses.map((course, idx) => (
                            <div key={`${course.id}-${semester}-${idx}`} className={getColSpanClass(course.units)}>
                                <CourseCard {...course} />
                            </div>
                        ))}
                        {emptySlots > 0 && Array.from({ length: emptySlots }).map((_, i) => (
                            <div key={`empty-${semester}-${i}`} className={getColSpanClass(2)}>
                                <EmptyCourseCard />
                            </div>
                        ))}
                    </div>
                    {overloadCourses.length > 0 && (
                        <div className="my-4 w-full rounded border-t-2 border-red-500 border-dotted">
                            <div className="space-y-2 mt-4">
                            <div className="flex items-center gap-1">
                                    <div>Overloaded Courses</div>
                                    <ArrowDownIcon className="h-3 ml-1" />
                                </div>
                                <div className="grid grid-cols-8 w-full gap-2">
                                    {overloadCourses.map((course, idx) => (
                                        <div key={`${course.id}-ov-${semester}-${idx}`} className={getColSpanClass(course.units * 2)}>
                                            <CourseCard {...course} />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default function Courses() {
    const courses = [
        {name: "Computer Systems Principles and Programming", id: "CSSE2310", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20252, completed: false},
        {name: "Database Systems", id: "CSSE2002", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20252, completed: false},
        {name: "Software Engineering", id: "CSSE2003", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20252, completed: false},
        {name: "Algorithms and Data Structures", id: "CSSE2004", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20252, completed: false},
        {name: "Operating Systems", id: "CSSE2310", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20261, completed: false},
        {name: "Advanced Programming", id: "CSSE2002", units: 4, degreeReq: "Software Engineering Core Courses", sem: 20261, completed: false},
        {name: "Mathematics", id: "MATH1001", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20261, completed: false},
        {name: "Mathematics", id: "MATH1001", units: 1, degreeReq: "Software Engineering Core Courses", sem: 20261, completed: false},
        {name: "Mathematics", id: "MATH1001", units: 2, degreeReq: "Software Engineering Core Courses", sem: 20262, completed: false},
    ]

    const coursesBySemester = courses.reduce((acc, course) => {
        if (!acc[course.sem]) {
            acc[course.sem] = [];
        }
        acc[course.sem].push(course);
        return acc;
    }, {} as Record<number, CourseInfo[]>);

    return (
        <div className="flex flex-col h-screen overflow-y-auto">
            {Object.entries(coursesBySemester).map(([key, cs]) => (
                <SemesterSection key={key} semester={+key} courses={cs} />
            ))}
        </div>
    );
}
