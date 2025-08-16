"use client";
import React, { useState, useEffect } from 'react';
import CourseCard, { EmptyCourseCard } from "@/components/custom/course-card";
import { ArrowDownIcon, ChevronDownIcon } from "@heroicons/react/20/solid";

import Pop from '@/components/custom/palette'

import {DndContext, DragEndEvent} from '@dnd-kit/core';
import { Course } from '@/types/course';
import { v4 as uuidv4 } from "uuid";
function SemesterSection({ semester, courses, setPaletteOpen, setActiveId }:
    { semester: number; courses?: Course[], setPaletteOpen: (open: boolean) => void,
      setActiveId: (id: string) => void}) {
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
                            <CourseCard {...course} />
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
    const [isPaletteOpen, setPaletteOpen] = useState(false);
    const [sem, setSem] = useState(undefined);
    function handleDragEnd(event: DragEndEvent) {
      const { active, over } = event;

      if (!over) return;

      const dragCourse = active.data.current as Course;
      if (!dragCourse) return;

      const [targetSemIndexStr, targetIndexStr] = over.id.toString().split("-");
      const year = Math.floor(Number(targetSemIndexStr) / 10);
      const semNum = Number(targetSemIndexStr) % 10;
      const targetSemIndex = (year - startYear) * 2 + (semNum - 1);
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
      const targetSemIndex = (year - startYear) * 2 + (semNum - 1);
      const targetIndex = parseInt(targetIndexStr, 10);

      setCourses(prevCourses => {
        const newCourses = prevCourses.map(sem => [...sem]);

        const updatedCourse = { ...course, sem: targetId, id: uuidv4()};
        newCourses[targetSemIndex].splice(targetIndex, 1, updatedCourse); // replace empty card

        console.log("insert", newCourses)
        return newCourses;
      });
      setActiveId("");
    };


    const [activeId, setActiveId] = useState<string>("");
    const startYear = 2024;
    const endYear = 2026; // example
    useEffect(() => {
        console.log("id change: ", activeId);
    });
    const semesters: number[] = [];
    const tmpCourses: Course[][] = [];
    for (let year = startYear; year <= endYear; year++) {
      semesters.push(Number(`${year}1`));
      semesters.push(Number(`${year}2`));
      tmpCourses.push([]);
      tmpCourses.push([]);
    }
    const [stateCourses, setCourses] = useState<Course[][]>(tmpCourses);

    return (
      <DndContext
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
        />

        <div className="flex flex-col h-screen overflow-y-auto">
          {semesters.map((semester, i) => (
            <SemesterSection
              key={semester}
              semester={semester}
              courses={stateCourses[i]}
              setPaletteOpen={setPaletteOpen}
              setActiveId={setActiveId}
            />
          ))}
        </div>
      </DndContext>
    );
}
