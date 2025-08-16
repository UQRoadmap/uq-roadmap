import { EllipsisVerticalIcon, StarIcon, PlusIcon } from "@heroicons/react/20/solid";
import Droppable from "@/components/droppable"
import Draggable from "@/components/draggable"
import { Badge } from '@/components/badge'
import { Checkbox, CheckboxField, CheckboxGroup } from '@/components/checkbox'
import { Description, Fieldset, Label } from '@/components/fieldset'

import { Course, DegreeReq } from '@/types/course'
import { useState } from "react";
import { createPortal } from "react-dom";

export type CourseExtended = Course & {
  deleteMeth: (id: string, sem: string) => void
}

export default function CourseCard({id, code, name, units, sems, sem, secats, desc, degreeReq, completed, deleteMeth}: CourseExtended) {
    const [popupOpen, setPopupOpen] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalData, setModalData] = useState<Course | null>(null); // store the course whose details you want

    function handleDelete() {
      console.log("Delete course:", id, sem);
      deleteMeth(id, sem);
      setPopupOpen(false);
    }

    function handleDets() {
      setModalData({id, code, name, units, sem, sems, secats, desc, degreeReq, completed});  // pass in the course whose details to show
      setPopupOpen(false);
      setIsModalOpen(true);
    }

    function getCourseCategories(courseCode: string, reqs: DegreeReq): string[] {
      return Object.entries(reqs)
        .filter(([_, codes]) => codes.includes(courseCode))
        .map(([category]) => category.charAt(0).toUpperCase() + category.slice(1));
    }

    const categories = getCourseCategories(code, degreeReq);
    console.log(categories)
    return (
      <Draggable
        id={id}
        key={id}
        data={{id, code, name, units, sem, sems, secats, desc, degreeReq, completed}}
        disabled={false}
      >
        <Droppable key={id} id={id} full>
            <div
            className="hover:cursor-grab bg-white box-border h-30 flex flex-col justify-between rounded-lg border border-gray-400 shadow-md overflow-hidden"
            key={id}
            >
                <div className="bg-tertiary p-2 space-y-1 flex justify-between align-center h-9">
                <div className="text-sm space-y-2 text-white">
                  {categories.length > 0 ? (
                    <h1 className="">{categories.join(", ")}</h1>
                  ) : (
                    <p>No categories</p>
                  )}
                </div>
                <div className="relative">
                  <EllipsisVerticalIcon
                    className="h-4 text-white hover:cursor-pointer"
                    data-no-dnd="true"
                    onClick={(e) => { e.stopPropagation(); setPopupOpen((prev) => !prev);}}
                  />
                  {popupOpen && (
                    <div className="absolute right-0 mt-2 w-24 bg-white border border-gray-300 rounded shadow-lg z-100">
                      <button
                        onClick={(e) => {e.stopPropagation(); handleDets();}}
                        className="w-full text-left px-2 py-1 text-yellow-600 hover:bg-gray-100"
                      >
                        Details
                      </button>
                      <button
                        onClick={(e) => {e.stopPropagation(); handleDelete();}}
                        className="w-full text-left px-2 py-1 text-red-600 hover:bg-gray-100"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
                  <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
                    {modalData && (
                      <div className="flex, flex-col space-y-5">
                        <h2 className="text-2xl font-bold mb-4">{modalData.name}</h2>
                        <p><strong>Code:</strong> {modalData.code}</p>
                        <p><strong>Units:</strong> {modalData.units}</p>
                        <p className="space-y-5" ><strong>Semesters:</strong> {modalData.sems.join(", ")}</p>
                        <Fieldset className="space-y-5 rounded-lg p-4 bg-gray-50">
                          <CategoryDropdown categories={getCourseCategories(code, degreeReq)}/>
                          <CheckboxGroup className="space-y-2">
                            <CheckboxField className="flex items-start space-x-3">
                              <Checkbox
                                name="override"
                                value="override"
                                className="mt-1 h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                              />
                              <div className="flex flex-col">
                                <Label className="font-medium text-gray-900 cursor-pointer">
                                  Override
                                </Label>
                                <Description className="text-gray-500 text-sm">
                                  You can use this option to override settings or semesters if the
                                  course has recently changed and UQ is yet to update it.
                                </Description>
                              </div>
                            </CheckboxField>
                          </CheckboxGroup>
                        </Fieldset>
                        <p><strong>Description:</strong> {modalData.desc}</p>
                      </div>
                    )}
                  </Modal>
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

export function PaletteCourseCard({id, code, name, units, sem, sems, secats, desc, degreeReq, completed}: Course) {
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

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

function Modal({ isOpen, onClose, children }: ModalProps) {
  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-9999 flex items-center justify-center bg-black/50">
      <div className="bg-white p-6 rounded-lg w-3/4 max-w-3xl max-h-[90vh] overflow-auto shadow-lg">
        {children}
      </div>
    </div>,
    document.body // portal renders modal at the root of the document
  );
}


function CategoryDropdown({ categories }: { categories: string[] }) {
  const [selected, setSelected] = useState("");

  return (
    <div className="w-64">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Select Category
      </label>
      <select
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        className="block w-full rounded-md border border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
      >
        <option value="" disabled>
          -- Choose a category --
        </option>
        {categories.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>
    </div>
  );
}
