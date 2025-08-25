import { useState } from "react";

import { Draggable } from '@hello-pangea/dnd';

import { EllipsisVerticalIcon, StarIcon, PlusIcon } from "@heroicons/react/20/solid";
import { Badge } from '@/components/badge'

import OverviewModal from '@/components/custom/overview'

import { Course, Prereq,  DegreeReq, Secat, AssessmentItem } from '@/types/course'

type CourseKey = Course & {
    dragKey: string,
}

export type CourseExtended = CourseKey & {
    deleteMeth: (id: string, sem: string) => void,
    pos: number,
}

export default function CourseCard({id, code, name, units, sems, sem,
   secats, desc, degreeReq, completed, deleteMeth, pos, dragKey}: CourseExtended) {

    const [popupOpen, setPopupOpen] = useState<boolean>(false);
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    // store the course whose details you want
    const [modalData, setModalData] = useState<Course | null>(null);

    const categories = getCourseCategories(code, degreeReq);
    function handleDelete() {
      console.log("Delete course:", id, sem);
      deleteMeth(id, sem);
      setPopupOpen(false);
    }

    function handleDets() {
      setModalData({id, code, name, units, sem,
         sems, secats, desc, degreeReq, completed});
        // pass in the course whose details to show
      setPopupOpen(false);
      setIsModalOpen(true);
    }

    return (
      <Draggable draggableId={dragKey} index={pos}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps} // container props
            {...provided.dragHandleProps}
            className="bg-tertiary p-2 space-y-1 rounded shadow"
          >
            {/* Drag handle only here */}
            <div
              className="flex justify-between align-center h-9 cursor-grab"
            >
              <div className="text-sm text-white">
                {name} ({code})
              </div>
            </div>

            {/* Action menu + modal NOT draggable */}
            <div className="relative">
              <EllipsisVerticalIcon
                className="h-4 text-white hover:cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  setPopupOpen((prev) => !prev);
                }}
              />
              {popupOpen && (
                <div className="absolute right-0 mt-2 w-24 bg-white border border-gray-300 rounded shadow-lg z-100">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDets();
                    }}
                    className="w-full text-left px-2 py-1 text-yellow-600 hover:bg-gray-100"
                  >
                    Details
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete();
                    }}
                    className="w-full text-left px-2 py-1 text-red-600 hover:bg-gray-100"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>

            <OverviewModal
              isModalOpen={isModalOpen}
              setIsModalOpen={setIsModalOpen}
              modalData={modalData}
            />
          </div>
        )}
      </Draggable>
    )
}

export function getCourseCategories(courseCode: string, reqs: DegreeReq): string[] {
  return Object.entries(reqs)
    .filter(([_, codes]) => codes.includes(courseCode))
    .map(([category]) => category.charAt(0).toUpperCase() + category.slice(1));
}

export function EmptyCourseCard({degreeReq, id, setPaletteOpen, setActiveId}:
    {degreeReq?: string, id: string, setPaletteOpen: (open: boolean) => void,
     setActiveId: (targetId: string) => void }) {
    return (
          <div
              className="hover:cursor-pointer relative box-border h-30 flex flex-col justify-between rounded-lg border border-dashed border-gray-400 shadow-md overflow-hidden"
          >
              {/* Overlay to dim entire card with interactive icon */}
              <div className="absolute inset-0 bg-gray-500/50 z-10 rounded-lg flex items-center justify-center"
                    onClick={() => { setPaletteOpen(true); setActiveId(id.toString()); }}
              >
                  <PlusIcon className="h-6 w-6 text-white" />
              </div>
              <div className="text-xs font-medium truncate p-2">

              </div>
              <div className="text-xs flex items-center justify-between w-full p-2">
                  <div className="truncate">

                  </div>
                  <div>

                  </div>
                  <div className="flex items-center space-x-1 text-yellow-400">

                  </div>
              </div>
              <div className="text-xs mt-2 truncate flex justify-between w-full" title={degreeReq}>
              </div>
          </div>
    )
}

export function PaletteCourseCard
({id, code, name, units, sem, sems, secats, desc, degreeReq, completed}: Course) {
    return (
        <li
          className="group cursor-move rounded-md px-3 py-2 bg-gray-800 hover:bg-gray-700 transition-colors flex flex-col select-none z-[9999]"
        >
          <div className="flex justify-between items-center">
            <span className="ml-3 flex-auto truncate text-gray-300 text-lg">{code} - {name}</span>
            <span className="ml-3 hidden flex-none text-gray-400 group-data-focus:inline">Add to planner</span>
          </div>
          <span className="ml-3 text-gray-400 text-sm">{desc.length > 180 ? desc.slice(0, 180) + '…' : desc}</span>
          <span className="ml-3 text-gray-400 text-sm space-x-2">
            {sems.map((sem) => {
              return (
                <Badge key={sem} color="purple">
                  {sem}
                </Badge>
              );
            })}
              <Badge color="pink">{units} Units</Badge>
              <Badge color={secats > 3.5 ? "green" : secats > 2 ? "orange" : "red"}>
                  <div className="flex items-center space-x-1 text-yellow-400">
                    <span>{secats}</span>
                    <StarIcon className="w-3 h-3" />
                  </div>
              </Badge>
          </span>
        </li>
    )
}
