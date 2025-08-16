"use client";
import React, { useState } from 'react';
import CourseCard, { EmptyCourseCard } from "@/components/custom/course-card";
import { ArrowDownIcon, ChevronDownIcon } from "@heroicons/react/20/solid";

import Pop from '@/components/custom/palette'

import {DndContext, DragEndEvent} from '@dnd-kit/core';
import { Course } from '@/types/course';

function SemesterSection({ semester, courses }: { semester: number; courses: Course[] }) {
    const [collapsed, setCollapsed] = useState(false);

    let usedUnits = 0;
    const normalCourses: Course[] = [];
    const overloadCourses: Course[] = [];
    courses.forEach(course => {
        if (usedUnits + course.units <= 8) {
            normalCourses.push(course);
            usedUnits += course.units;
        } else {
            overloadCourses.push(course);
        }
    });


    const getSemesterLabel = (sem: number) => {
        const year = Math.floor(sem / 10);
        const semesterNum = sem % 10;
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
                    className={`w-5 h-5 transform transition-transform text-black hover:bg-gray-800 rounded-xl ${collapsed ? 'rotate-180' : ''}`}
                    onClick={() => setCollapsed(prev => !prev)}
                />
            </div>
            {!collapsed && (
                <>
                    <div className="grid grid-cols-8 w-full gap-2">
                        {normalCourses.map((course, idx) => (
                            <div key={`${course.id}-${semester}-${idx}`} className={getColSpanClass(course.units)}>
                                <CourseCard {...course} key={semester + idx} />
                            </div>
                        ))}
                        <div key={`empty-${semester}`} className={getColSpanClass(2)}>
                            <EmptyCourseCard id={semester}/>
                        </div>
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
    function handleDragEnd(event: DragEndEvent) {
      const {active, over} = event;
      console.log(active)
      if (over) {
        const dragCourse = active.data.current as Course;
        if (dragCourse) {
          const updatedCourse = { ...dragCourse, sem: over.id.toString()};
          setCourses((prevCourses) => [
            ...prevCourses.filter(c => c.id !== dragCourse.id),
            updatedCourse
          ]);
        }
      }
      setActiveId(undefined);
    }

    const [activeId, setActiveId] = useState<string | undefined>(undefined);
    const [stateCourses, setCourses] = useState<Course[]>([]);

    const startYear = 2024;
    const endYear = 2026; // example

    const semesters: number[] = [];
    for (let year = startYear; year <= endYear; year++) {
      semesters.push(Number(`${year}1`));
      semesters.push(Number(`${year}2`));
    }

    return (
      <DndContext
        onDragStart={({ active }) => setActiveId(active.id as string)}
        onDragEnd={handleDragEnd}
      >
        <Pop draggable activeId={activeId}></Pop>
        <div className="flex flex-col h-screen overflow-y-auto">
          {semesters.map((semester) => (
            <SemesterSection
              key={semester}
              semester={semester}
              courses={stateCourses.filter(c => +c.sem === semester)}
            />
          ))}
        </div>
      </DndContext>
    );
}
