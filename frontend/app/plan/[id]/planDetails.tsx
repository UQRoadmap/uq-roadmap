"use client";
import React, { useState } from 'react';
import CourseCard, { EmptyCourseCard } from "@/components/custom/course-card";
import { ChevronDownIcon } from "@heroicons/react/20/solid";
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from '@/components/dropdown';
import Pop from '@/components/custom/palette'

import { DragDropContext, Droppable, DropResult } from "@hello-pangea/dnd";
import { Course, DegreeReq } from '@/types/course';
import ProgressCircle from '@/components/custom/progressCircle';
import { PlannedCourses, Plan, CourseData } from '@/types/plan';

function SemesterSection({
  semesterId,
  courses,
  setPaletteOpen,
  setActiveId,
  setDelete,
  courseReqs
}: {
  semesterId: string; // e.g. "2025-1"
  courses: Course[];
  setPaletteOpen: (open: boolean) => void,
  setActiveId: (id: string) => void,
  setDelete: (id: string, sem: string) => void,
  courseReqs: DegreeReq
}) {
  const [collapsed, setCollapsed] = useState(false);

  const getSemesterLabel = (semId: string) => {
    const [year, sem] = semId.split("-");
    return `${year} Semester ${sem}`;
  };

  return (
    <div key={semesterId} className="flex flex-col gap-4 w-full p-4">
      <div className="flex justify-between items-center cursor-pointer">
        <div>{getSemesterLabel(semesterId)}</div>
        <ChevronDownIcon
          className={`w-5 h-5 transform transition-transform text-black hover:bg-gray-300 rounded-xl ${collapsed ? 'rotate-180' : ''}`}
          onClick={() => setCollapsed(prev => !prev)}
        />
      </div>
      {!collapsed && (
        <Droppable droppableId={semesterId} direction="horizontal">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="grid grid-cols-8 w-full gap-2"
            >
              {courses.map((course) => (
                <div
                  key={course.id}
                  className={`col-span-${course.units ?? 2}`}
                >
                  <CourseCard
                    {...course}
                    deleteMeth={setDelete}
                    degreeReq={courseReqs}
                  />
                </div>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      )}
    </div>
  );
}


export function PlanDetailClient({
  initialPlan,
  courses
}: {
  initialPlan: Plan,
  courses: Course[]
}) {
  const [plan, setPlan] = useState<Plan>(initialPlan);
  const [isPaletteOpen, setPaletteOpen] = useState(false);
  const [activeId, setActiveId] = useState<string | undefined>();
  const [sem, setSem] = useState<string | undefined>();

  const courseReqs: DegreeReq = {
    core: ["csse2310", "csse2010", "CSSE6400"],
    electives: ["DATA2001", "CSSE6400"],
  };

  const handleDragEnd = (result: DropResult) => {
    const { source, destination } = result;
    if (!destination) return;

    const sourceSem = source.droppableId; // "2025-1"
    const destSem = destination.droppableId;

    // Same semester → reorder
    if (sourceSem === destSem) {
      const updated = Array.from(plan.courses[sourceSem].sem);
      const [moved] = updated.splice(source.index, 1);
      updated.splice(destination.index, 0, moved);

      // Reassign pos
      const reordered = updated.map((c, i) => ({ ...c, pos: i }));
      setPlan({
        ...plan,
        courses: {
          ...plan.courses,
          [sourceSem]: { sem: reordered },
        },
      });
    } else {
      // Cross-semester move
      const sourceList = Array.from(plan.courses[sourceSem].sem);
      const destList = Array.from(plan.courses[destSem].sem);

      const [moved] = sourceList.splice(source.index, 1);
      destList.splice(destination.index, 0, { ...moved, pos: destination.index });

      const reorderedSource = sourceList.map((c, i) => ({ ...c, pos: i }));
      const reorderedDest = destList.map((c, i) => ({ ...c, pos: i }));

      setPlan({
        ...plan,
        courses: {
          ...plan.courses,
          [sourceSem]: { sem: reorderedSource },
          [destSem]: { sem: reorderedDest },
        },
      });
    }
  };

  return (
    <div>
      <div className="bg-secondary py-4 overflow-y-auto">
        <div className="max-w-7xl px-8 mx-auto flex items-center justify-between w-full">
          <div>
            <div className='flex items-center gap-x-6 gap-y-2'>
              <div className='text-white text-lg'>{plan.name}</div>
              <div className='ml-2'>
                <Dropdown>
                  <DropdownButton accent>
                    Options <ChevronDownIcon />
                  </DropdownButton>
                  <DropdownMenu>
                    <DropdownItem onClick={() => setPlan(p => ({ ...p, reversed: !p.courses.reversed }))}>
                      Reverse Sorting
                    </DropdownItem>
                  </DropdownMenu>
                </Dropdown>
              </div>
            </div>
            <div className='my-4 text-xl text-white'>{plan.degree.title}</div>
            <div className='flex text-white italic'>
              Planned Completion Date: {plan.end_year} Semester {plan.start_sem}
            </div>
          </div>
          <ProgressCircle percentage={plan.percentage ?? 0} />
        </div>
      </div>

      <div className='max-w-7xl mx-auto px-4'>
        <DragDropContext onDragEnd={handleDragEnd}>
          <Pop
            clickable
            setActiveId={setActiveId}
            activeId={activeId}
            opened={isPaletteOpen}
            setPaletteOpen={setPaletteOpen}
            sem={sem}
            setDelete={() => { }}
            courseReqs={courseReqs}
            courses={courses}
          />

          <div className="flex flex-col h-screen overflow-y-auto">
            {Object.entries(plan.courses).map(([semesterId, data]) => {
              const semesterCourses: Course[] = data.sem
                .sort((a, b) => a.pos - b.pos)
                .map(cd => courses.find(c => c.id === cd.code))
                .filter((c): c is Course => c !== undefined);

              return (
                <SemesterSection
                  key={semesterId}
                  semesterId={semesterId}
                  courses={semesterCourses}
                  setPaletteOpen={setPaletteOpen}
                  setActiveId={setActiveId}
                  setDelete={() => { }}
                  courseReqs={courseReqs}
                />
              );
            })}
          </div>

        </DragDropContext>
      </div>
    </div>
  );
}
