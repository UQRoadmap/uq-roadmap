'use client'

import {
  Combobox,
  ComboboxInput,
  Dialog,
  DialogPanel,
  DialogBackdrop,
} from '@headlessui/react'
import OverviewModal from '@/components/custom/overview'
import CourseCard from '@/components/custom/course-card'
import { StarIcon, EyeIcon } from "@heroicons/react/20/solid"
import {DragOverlay} from '@dnd-kit/core';
import Draggable from '@/components/draggable'
import { useState, useMemo } from 'react'
import { Course, DegreeReq } from '@/types/course'
import { MagnifyingGlassIcon } from '@heroicons/react/16/solid';

// react-window
import { FixedSizeList as List, ListChildComponentProps } from 'react-window';

export default function CommandPalette({
  draggable, clickable, setActiveId, activeId, opened, sem,
  setPaletteOpen, onSelectCourse, stateCourses, setDelete, courseReqs, courses
}: {
  draggable?: boolean, clickable?: boolean, setActiveId: (open: string) => void,
  activeId: string, opened: boolean, sem?: string, setPaletteOpen: (open: boolean) => void,
  onSelectCourse: (course: Course, id: string) => void, stateCourses: Course[][],
  setDelete: (id: string, sem:string) => void, courseReqs:DegreeReq, courses: Course[]
}) {
  const [query, setQuery] = useState('')
  const [modalCourse, setModalCourse] = useState<Course | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const activeCourse = courses.find(c => c.id === activeId) as Course;

  // memoize filtering to avoid re-runs
  const filteredcourses = useMemo(() => {
    const q = query.toLowerCase();
    return courses.filter((course) =>
      course.name.toLowerCase().includes(q) ||
      course.code.toLowerCase().includes(q)
    );
  }, [query, courses]);

  const handleOpenModal = (course: Course) => {
    setModalCourse(course)
    setIsModalOpen(true)
  }

  const handleClick = (course: Course) => {
    if (!clickable) return;
    course.sem = sem ?? "";
    setActiveId(course.id)
    if (onSelectCourse) {
      onSelectCourse(course, activeId); // pass the course and the target slot id
    }
    setPaletteOpen(false);
    setQuery('');
  };

  // virtualized row renderer
  const Row = ({ index, style }: ListChildComponentProps) => {
    const course = filteredcourses[index];
    return (
      <div style={style}>
        <Draggable id={course.id} key={course.id} data={course} disabled={!draggable}>
          <li
            className={`group ${clickable ? "cursor-pointer" : "cursor-grab"}
              rounded-md px-3 py-2 backdrop-blur-md bg-[#1f1f1f]
              hover:bg-[#1f1f1f] transition-colors flex flex-col select-none`}
            onClick={() => handleClick(course)}
            style={{ opacity: activeId === course.id ? 0 : 1 }}
          >
            <div className="flex justify-between items-center">
              <span className="ml-3 flex-auto truncate text-lg">
                {course.code} - {course.name}
              </span>
              <button
                className="absolute right-2 top-2 opacity-0 group-hover:opacity-100
                  transition-opacity p-1 rounded hover:bg-gray-700"
                onClick={(e) => { e.stopPropagation(); handleOpenModal(course) }}
                title="View Details"
              >
                <EyeIcon className="h-5 w-5 text-blue-400" />
              </button>
            </div>
            <span className="ml-3 text-gray-400 text-sm">
              {course.desc.length > 180 ? course.desc.slice(0, 180) + '…' : course.desc}
            </span>
            <div className="flex ml-3 text-gray-400 text-sm justify-between">
              <div>
                <span className="font-semibold">Offerings: {course.sems?.join(', ')}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span>{course.units} Units</span>
                <div className="flex items-center space-x-1 text-yellow-400">
                  <span>{course.secats}</span>
                  <StarIcon className="w-3 h-3" />
                </div>
              </div>
            </div>
          </li>
        </Draggable>
      </div>
    )
  }

  return (
    <div>
      <Dialog
        className="relative z-10"
        open={opened}
        onClose={() => { setPaletteOpen(false); setQuery('') }}
      >
        <div className="fixed inset-0 z-10 w-screen overflow-y-auto p-4 sm:p-6 md:p-20 transition ease-in-out duration-300">
          <DialogBackdrop className="fixed inset-0 bg-black/20 backdrop-blur-sm"
            style={{ opacity: opened ? 1 : 0, transition: 'opacity 200ms ease-in-out' }}
          />

          <DialogPanel
            transition
            className="mx-auto max-w-2xl transform divide-y divide-white/10 overflow-hidden
              rounded-xl bg-black/60 shadow-2xl outline-1 -outline-offset-1 outline-white/10
              backdrop-blur-sm backdrop-filter transition-all
              data-closed:scale-95 data-closed:opacity-0
              data-enter:duration-300 data-enter:ease-out
              data-leave:duration-200 data-leave:ease-in"
          >
            <Combobox>
              <div className="flex items-center gap-3 px-3">
                <MagnifyingGlassIcon className="h-5 w-5 text-white" />
                <ComboboxInput
                  autoFocus
                  className="flex-1 h-12 bg-transparent pr-4 text-base text-white
                    placeholder:text-white sm:text-sm outline-none"
                  placeholder="Search courses..."
                  onChange={(event) => setQuery(event.target.value)}
                />
              </div>

              {(query === '' || filteredcourses.length > 0) && (
                <div className="max-h-80 overflow-y-auto">
                  <List
                    height={320} // height of the list container
                    itemCount={filteredcourses.length}
                    itemSize={120} // row height in px
                    width="100%"
                    className={`group ${clickable ? "cursor-pointer" : "cursor-grab"} rounded-md px-3 py-2 backdrop-blur-lg bg-gray text-white transition-colors flex flex-col select-none`}
                  >
                    {Row}
                  </List>
                </div>
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

      <DragOverlay className="z-50">
        {activeId && (
          <CourseCard {...stateCourses.flat().find(c => c.id === activeId)!}
            deleteMeth={setDelete} degreeReq={courseReqs}
          />
        )}
      </DragOverlay>

      {modalCourse && (
        <OverviewModal isModalOpen={isModalOpen}
          setIsModalOpen={setIsModalOpen}
          modalData={modalCourse}
        />
      )}
    </div>
  )
}
