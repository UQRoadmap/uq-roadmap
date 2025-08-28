"use client";
import React, { useState } from "react";
import { v4 as uuidv4 } from "uuid";

import CourseCard, { EmptyCourseCard } from "@/components/custom/course-card";
import { ChevronDownIcon } from "@heroicons/react/20/solid";
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from "@/components/dropdown";
import Pop from "@/components/custom/palette";

import { DragDropContext, Droppable, DropResult } from "@hello-pangea/dnd";
import { Course, DegreeReq } from "@/types/course";
import ProgressCircle from "@/components/custom/progressCircle";
import { Plan, CourseData, PlannedCourses } from "@/types/plan";

// Same as CourseData but stores the draggableId for swaps
type LocalCourseData = CourseData & {
  instanceId: string;
};

type CourseKey = Course & {
  dragKey: string;
  pos: number;
};

function SemesterSection({
  semesterId,
  courses,
  setPaletteOpen,
  setActiveId,
  setDelete,
  courseReqs,
}: {
  semesterId: string;
  courses: CourseKey[];
  setPaletteOpen: (open: boolean) => void;
  setActiveId: (id: string) => void;
  setDelete: (id: string, sem: string) => void;
  courseReqs: DegreeReq;
}) {
  const [collapsed, setCollapsed] = useState(false);

  const getSemesterLabel = (semId: string) => {
    const [year, sem] = semId.split("-");
    return `${year} Semester ${sem}`;
  };

  return (
    <div className="flex flex-col gap-4 w-full p-4">
      <div className="flex justify-between items-center cursor-pointer">
        <div>{getSemesterLabel(semesterId)}</div>
        <ChevronDownIcon
          className={`w-5 h-5 transform transition-transform ${collapsed ? "rotate-180" : ""}`}
          onClick={() => setCollapsed((prev) => !prev)}
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
              {courses.map((course, i) => (
                <CourseCard
                  key={course.dragKey}
                  {...course}
                  deleteMeth={setDelete}
                  degreeReq={courseReqs}
                  pos={i}
                />
              ))}

              <EmptyCourseCard
                id={semesterId}
                setPaletteOpen={setPaletteOpen}
                setActiveId={setActiveId}
              />

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
  courses,
}: {
  initialPlan: Plan;
  courses: Course[];
}) {
  const [plan, setPlan] = useState<Plan>(initialPlan);
  const [isPaletteOpen, setPaletteOpen] = useState(false);
  const [activeId, setActiveId] = useState<string>();
  const [sem, setSem] = useState<string>();

  const courseReqs: DegreeReq = {
    core: ["csse2310", "csse2010", "CSSE6400"],
    electives: ["DATA2001", "CSSE6400"],
  };

  const findCourse = (code: string) => courses.find((c) => c.id === code) || null;

  const getSemList = (semesterId: string): LocalCourseData[] =>
    ((plan.courses as PlannedCourses)[semesterId]?.sem || []) as LocalCourseData[];

  const setSemList = (semesterId: string, list: LocalCourseData[]) => {
    setPlan((prev) => ({
      ...prev,
      courses: {
        ...prev.courses,
        [semesterId]: { sem: list as unknown as CourseData[] },
      },
    }));
  };

  const addCourse = (course: Course, semesterId: string) => {
    const list = getSemList(semesterId);
    const newItem: LocalCourseData = {
      code: course.id,
      pos: list.length,
      instanceId: uuidv4(),
      part_id: "0", // TODO: Maybe change this
    };
    setSemList(semesterId, [...list, newItem]);
  };

  const removePlannedByInstance = (semesterId: string, instanceId: string) => {
    const list = getSemList(semesterId).filter((x) => x.instanceId !== instanceId);
    // reassign positions
    const rePos = list.map((c, i) => ({ ...c, pos: i }));
    setSemList(semesterId, rePos);
  };

  const handleDragEnd = (result: DropResult) => {
    const { source, destination } = result;
    if (!destination) return;

    const sourceSem = source.droppableId;
    const destSem = destination.droppableId;

    const sourceList = [...getSemList(sourceSem)];
    const destList = sourceSem === destSem ? sourceList : [...getSemList(destSem)];

    // remove from source
    const [moved] = sourceList.splice(source.index, 1);

    if (!moved) return;

    // insert into destination
    destList.splice(destination.index, 0, moved);

    if (sourceSem === destSem) {
      // reorder within same semester
      const rePos = destList.map((c, i) => ({ ...c, pos: i }));
      setSemList(sourceSem, rePos);
    } else {
      // move across semesters
      const rePosSource = sourceList.map((c, i) => ({ ...c, pos: i }));
      const rePosDest = destList.map((c, i) => ({ ...c, pos: i }));
      setSemList(sourceSem, rePosSource);
      setSemList(destSem, rePosDest);
    }
  };

  const hydrateSemester = (semesterId: string): CourseKey[] => {
    return getSemList(semesterId)
      .slice()
      .sort((a, b) => a.pos - b.pos)
      .map((cd) => {
        const course = findCourse(cd.code);
        if (!course) return null;
        return {
          ...course,
          dragKey: cd.instanceId,
          pos: cd.pos,
        } as CourseKey;
      })
      .filter((x): x is CourseKey => x !== null);
  };

  return (
    <div>
      <div className="bg-secondary py-4">
        <div className="max-w-7xl px-8 mx-auto flex items-center justify-between w-full">
          <div>
            <div className="flex items-center gap-x-6">
              <div className="text-white text-lg">{plan.name}</div>
              <Dropdown>
                <DropdownButton accent>
                  Options <ChevronDownIcon />
                </DropdownButton>
                <DropdownMenu>
                  <DropdownItem
                    onClick={() =>
                      setPlan((p) => ({ ...p, reversed: !p.courses.reversed }))
                    }
                  >
                    Reverse Sorting
                  </DropdownItem>
                </DropdownMenu>
              </Dropdown>
            </div>
            <div className="my-4 text-xl text-white">{plan.degree.title}</div>
            <div className="flex text-white italic">
              Planned Completion Date: {plan.end_year} Semester {plan.start_sem}
            </div>
          </div>
          <ProgressCircle percentage={plan.percentage ?? 0} />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4">
        <DragDropContext onDragEnd={handleDragEnd}>
          <Pop
            clickable
            setActiveId={setActiveId}
            activeId={activeId}
            opened={isPaletteOpen}
            setPaletteOpen={setPaletteOpen}
            sem={sem}
            setDelete={() => {}}
            courseReqs={courseReqs}
            courses={courses}
            onSelectCourse={addCourse}
          />

          <div className="flex flex-col">
            {Array.from(
              { length: plan.end_year - plan.degree.year + 1 },
              (_, i) => plan.degree.year + i
            )
              .map((year) =>
                ["1", "2"].map((semId) => {
                  const semesterKey = `${year}-${semId}`;
                  const semesterCourses = hydrateSemester(semesterKey);

                  return (
                    <SemesterSection
                      key={semesterKey}
                      semesterId={semesterKey}
                      courses={semesterCourses}
                      setPaletteOpen={setPaletteOpen}
                      setActiveId={setActiveId}
                      setDelete={() => {}}
                      courseReqs={courseReqs}
                    />
                  );
                })
              )
              .flat()}
          </div>
        </DragDropContext>
      </div>
    </div>
  );
}
