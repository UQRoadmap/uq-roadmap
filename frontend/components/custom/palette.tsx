'use client'

import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
  Dialog,
  DialogPanel,
  DialogBackdrop,
} from '@headlessui/react'
import { Badge } from '@/components/badge'
import  CourseCard from '@/components/custom/course-card'
//import { StarIcon } from "@heroicons/react/20/solid"

import {DragOverlay} from '@dnd-kit/core';
import Draggable from '@/components/draggable'
import { useState } from 'react'

import { Course } from '@/types/course'
import { MagnifyingGlassIcon } from '@heroicons/react/16/solid';

const courses: Course[] = [
  {
    code: "CSSE6400",
    id: "meow1",
    sem: "1",
    name: 'Software Architecture',
    units: 2,
    secats: 4,
    completed: false,
    desc: "Software systems are often composed of a heterogeneous network of inter-related systems. In this course you will build upon the knowledge and skills you have developed so far to learn how to design complex systems. This will include how these systems communicate and coordinate their responsibilities. You will learn design techniques to manage the complexity of large systems. You will learn how to assess and manage software risks (e.g.security, scalability, availability, resilience, robustness). You will apply these techniques to build a system composed of heterogeneous computing devices (e.g. mobile devices, servers, cloud-hosted services). You will learn how to apply systems thinking to design large-scale cyber-physical systems." },
  {
    code: "CSSE3200",
    id: "meow",
    sem: "2",
    name: 'Software Engineering Studio: Design, Implement and Test',
    units: 2,
    secats: 3,
    completed: false,
    desc: "Students work in teams on a studio-based software development project to gain an understanding of the processes, techniques and tools used to manage and deliver large, complex software systems. The course covers software engineering, design, project management and team work processes. Students will learn techniques and tools used to manage complex software projects. These techniques and tools will be applied to software design, verification and validation, configuration management and documentation." },
  {
    code: "CSSE3221",
    id: "meow2",
    sem: "1 & 2",
    name: 'Software Engineering Studio: Design, Implement and Test',
    units: 2,
    secats: 1,
    completed: false,
    desc: "Students work in teams on a studio-based software development project to gain an understanding of the processes, techniques and tools used to manage and deliver large, complex software systems. The course covers software engineering, design, project management and team work processes. Students will learn techniques and tools used to manage complex software projects. These techniques and tools will be applied to software design, verification and validation, configuration management and documentation." },
  {
    code: "CSSE3211",
    id: "meow3",
    sem: "1 & 2",
    name: 'Software Engineering Studio: Design, Implement and Test',
    units: 2,
    secats: 1,
    completed: false,
    desc: "Students work in teams on a studio-based software development project to gain an understanding of the processes, techniques and tools used to manage and deliver large, complex software systems. The course covers software engineering, design, project management and team work processes. Students will learn techniques and tools used to manage complex software projects. These techniques and tools will be applied to software design, verification and validation, configuration management and documentation." },
  {
    code: "CSSE3201",
    id: "meow4",
    sem: "1 & 2",
    name: 'Software Engineering Studio: Design, Implement and Test',
    units: 2,
    secats: 1,
    completed: false,
    desc: "Students work in teams on a studio-based software development project to gain an understanding of the processes, techniques and tools used to manage and deliver large, complex software systems. The course covers software engineering, design, project management and team work processes. Students will learn techniques and tools used to manage complex software projects. These techniques and tools will be applied to software design, verification and validation, configuration management and documentation." },
]

const recent = [courses[0]]

export default function CommandPalette({draggable, clickable, setActiveId, activeId, opened, sem, setPaletteOpen, onSelectCourse, stateCourses}:
    {draggable?: boolean, clickable?: boolean, setActiveId: (open: string) => void,
        activeId: string, opened: boolean, sem?: string, setPaletteOpen: (open: boolean) => void,
        onSelectCourse: (course: Course, id: string) => void, stateCourses: Course[][]}) {
  const [query, setQuery] = useState('')
  const activeCourse = courses.find(c => c.id === activeId) as Course;
  const filteredcourses: Course[] =
    query === ''
      ? []
      : courses.filter((course) => {
          const q = query.toLowerCase();
          return (
            course.name.toLowerCase().includes(q) ||
            course.code.toLowerCase().includes(q)
          );
        });

    const handleClick = (course: Course) => {
      if (!clickable) return;
      console.log(course)
      course.sem = sem ?? "";
      console.log("active", activeCourse)
      setActiveId(course.id)
      if (onSelectCourse) {
        onSelectCourse(course, activeId); // pass the course and the target slot id
      }
      setPaletteOpen(false);
      setQuery('');
    };

  return (
    <div>
    <Dialog
      className="relative z-10"
      open={opened}
      onClose={() => {
        setPaletteOpen(false)
        setQuery('')
      }}
    >
      <div
        className="fixed inset-0 z-10 w-screen overflow-y-auto p-4 sm:p-6 md:p-20 transition ease-in-out duration-300"
      >
        <DialogBackdrop
          className="fixed inset-0 bg-black/20 backdrop-blur-sm"
          style={{ opacity: opened ? 1 : 0, transition: 'opacity 200ms ease-in-out' }}
        />

        <DialogPanel
          transition
          className="mx-auto max-w-2xl transform divide-y divide-white/10 overflow-hidden my-100 rounded-xl bg-black/60 shadow-2xl outline-1 -outline-offset-1 outline-white/10 backdrop-blur-sm backdrop-filter transition-all data-closed:scale-95 data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in"
        >
          <Combobox
          >
        <div className="flex items-center gap-3 px-3">
          <MagnifyingGlassIcon className="h-5 w-5 text-white" />
          <ComboboxInput
            autoFocus
            className="flex-1 h-12 bg-transparent pr-4 text-base text-white placeholder:text-white sm:text-sm outline-none"
            placeholder="Search courses..."
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>

        {(query === '' || filteredcourses.length > 0) && (
          <ul
            className="max-h-80 scroll-py-2 divide-y divide-white/10 overflow-y-auto"
          >
            <li className="p-2">
          {query === '' && <h2 className="mt-4 mb-2 px-3 text-sm font-semibold text-white">Recent searches</h2>}
          <ul className="space-y-2 text-sm text-gray-300">
            {(query === '' ? recent : filteredcourses).map((course) => (
              <Draggable
            id={course.id}
            key={course.id}
            data={course}
            disabled={!draggable}
              >
            <li
              className={`group ${clickable ? "cursor-pointer" : "cursor-grab"} rounded-md px-3 py-2 bg-black hover:bg-[#1f1f1f] transition-colors flex flex-col select-none`}
              onClick={() => handleClick(course)}
              style={{
                opacity: activeId === course.id ? 0 : 1, // hide original while dragging
              }}
            >
              <div className="flex justify-between items-center">
                <span className="ml-3 flex-auto truncate text-lg">{course.code} - {course.name}</span>
                <span className="ml-3 hidden flex-none text-gray-400 group-data-focus:inline">Add to planner</span>
              </div>
              <span className="ml-3 text-gray-400 text-sm">{course.desc.length > 180 ? course.desc.slice(0, 180) + '…' : course.desc}</span>
              <span className="ml-3 text-gray-400 text-sm space-x-2">
              <Badge color={course.sem == "2" ? "blue" : course.sem == "1" ? "red" : "purple"}>Semester {course.sem}</Badge>
              <Badge color="pink">{course.units} Units</Badge>
              <Badge color={course.secats > 3.5 ? "green" : course.secats > 2 ? "orange" : "red"}>
                  <div className="flex items-center space-x-1 text-yellow-400">
                stars to go here
                  </div>
              </Badge>
              </span>
            </li>
              </Draggable>
            ))}
          </ul>
            </li>
            {query === '' && (
          <li className="p-2">
          </li>
            )}
          </ul>
        )}

        {query !== '' && filteredcourses.length === 0 && (
          <div className="px-6 py-14 text-center sm:px-14">
            <p className="mt-4 text-sm text-white">
          We couldn’t find any courses with that query. Please try again.
            </p>
          </div>
        )}
          </Combobox>
        </DialogPanel>
      </div>
    </Dialog>
<DragOverlay>
  {activeId && (
    <CourseCard {...stateCourses.flat().find(c => c.id === activeId)!} />
  )}
</DragOverlay>
    </div>
  )
}
