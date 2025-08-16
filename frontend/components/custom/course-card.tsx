import { EllipsisVerticalIcon, StarIcon, PlusIcon } from "@heroicons/react/20/solid";
import Droppable from "@/components/droppable"
import Draggable from "@/components/draggable"
import { Badge } from '@/components/badge'

import { Course } from '@/types/course'

export default function CourseCard({id, code, name, units, sem, secats, desc, degreeReq, completed}: Course) {
    console.log(units)
    return (
      <Draggable
        id={id}
        key={id}
        data={{id, code, name, units, sem, secats, desc, degreeReq, completed}}
        disabled={false}
      >
        <Droppable key={id} id={id} full>
            <div
            className="hover:cursor-grab bg-white box-border h-30 flex flex-col justify-between rounded-lg border border-gray-400 shadow-md overflow-hidden"
            key={id}
            >
                <div className="bg-red-400 p-2 space-y-1 flex justify-between align-center h-9">
                    <div className="text-xs font-medium truncate">
                        {degreeReq}
                    </div>
                    <div>
                        <EllipsisVerticalIcon className="h-3"/>
                    </div>
                </div>
                <div className="text-xs font-medium truncate p-2" title={name}>
                    {name}
                </div>
                <div className="text-xs flex items-center justify-between w-full p-2">
                    <div className="truncate">{code}</div>
                    <div>
                        {units} Units
                    </div>
                    <div className="flex items-center space-x-1 text-yellow-400">
                        <span>{secats}</span>
                        <StarIcon className="w-3 h-3" />
                    </div>
                </div>
                <div className="text-xs mt-2 truncate flex justify-between w-full" title={degreeReq}>
                </div>
            </div>
        </Droppable>

      </Draggable>
    )
}

export function EmptyCourseCard({degreeReq, id, setPaletteOpen, setActiveId}:
    {degreeReq?: string, id: string, setPaletteOpen: (open: boolean) => void,
     setActiveId: (targetId: string) => void }) {
    return (
        <Droppable key={id} id={id}
        >
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
        </Droppable>
    )
}

export function PaletteCourseCard({id, code, name, units, sem, secats, desc, degreeReq, completed}: Course) {
    return (
        <li
          className="group cursor-move rounded-md px-3 py-2 bg-gray-800 hover:bg-gray-700 transition-colors flex flex-col select-none"
        >
          <div className="flex justify-between items-center">
            <span className="ml-3 flex-auto truncate text-gray-300 text-lg">{code} - {name}</span>
            <span className="ml-3 hidden flex-none text-gray-400 group-data-focus:inline">Add to planner</span>
          </div>
          <span className="ml-3 text-gray-400 text-sm">{desc.length > 180 ? desc.slice(0, 180) + '…' : desc}</span>
          <span className="ml-3 text-gray-400 text-sm space-x-2">
              <Badge color={sem == "2" ? "blue" : sem == "1" ? "red" : "purple"}>Semester {sem}</Badge>
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
