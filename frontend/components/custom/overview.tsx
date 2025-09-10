import { createPortal } from "react-dom";
import { useState, useEffect } from "react";

import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { CalendarIcon, BookOpenIcon, TagIcon, ClipboardDocumentListIcon } from "@heroicons/react/24/outline";
import { Checkbox, CheckboxField, CheckboxGroup } from '@/components/checkbox'
import { Description, Fieldset, Label } from '@/components/fieldset'

import { Course, Prereq, DetailedCourse, DegreeReq, Secat, AssessmentItem } from '@/types/course'

import { getCourseCategories } from '@/components/custom/course-card'

export default function OverviewModal({ isModalOpen, setIsModalOpen, modalData }: {
  isModalOpen: boolean;
  setIsModalOpen: (val: boolean) => void;
  modalData: Course | null;
}) {
  const [activeTab, setActiveTab] = useState<"general" | "prereqs" | "secats" | "assessment">("general");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [courseDatas, setCourseData] = useState<DetailedCourse | null>(null);

    // Fetch plans on component mount
    useEffect(() => {
        fetchCourse();
    }, [modalData?.code]);

    const fetchCourse = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch(`/api/course/${modalData?.code}`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch plans');
            }

            const courseData: DetailedCourse = await response.json();
            console.log("dets",courseData)
            setCourseData(courseData);
        } catch (err) {
            console.error('Error fetching plans:', err);
            setError(err instanceof Error ? err.message : 'Failed to load plans');
        } finally {
            setLoading(false);
        }
    };
  if (!modalData) return null;
  return (
    <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
      <div className="flex flex-col space-y-5">
        <h2 className="text-2xl font-bold mb-4">{modalData.name}</h2>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-4">
          {["general", "prereqs", "secats", "assessment"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as typeof activeTab)}
              className={`px-4 py-2 -mb-px font-medium border-b-2 ${
                activeTab === tab ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === "general" && (
            <div>
              <div className="space-y-2">
                <p><strong>Code:</strong> {modalData.code}</p>
                <p><strong>Units:</strong> {modalData.units}</p>
                <p><strong>Semesters:</strong> {modalData.sems.join(", ")}</p>
                <p><strong>Description:</strong> {modalData.desc}</p>
              </div>
              <Fieldset className="space-y-5 rounded-lg p-4 bg-gray-50">
                <CategoryDropdown categories={getCourseCategories(modalData.code, modalData.degreeReq)} />
              </Fieldset>
              <Fieldset className="space-y-2 rounded-lg p-4 bg-gray-50">
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
            </div>
          )}

          {activeTab === "secats" && courseDatas && (
            <div> <SecatGraph secat={courseDatas.secat}/> </div>
          )}

          {activeTab === "prereqs" && courseDatas &&  (
            <PrereqDisplay prereq={courseDatas.prereq} code={courseDatas.code }/>
          )}

          {activeTab === "assessment" && courseDatas && (
            <div><AssessmentList assessment={courseDatas.assessment}/> </div>
          )}
        </div>
      </div>
    </Modal>
  );
}


function SecatGraph({ secat }: { secat: Secat | null | undefined }) {
  if (!secat || !secat.questions?.length) return <p>No data available</p>;

  const data = secat.questions.map(q => ({
    name: q.name,
    'Strongly Agree': q.s_agree,
    Agree: q.agree,
    Neutral: q.middle,
    Disagree: q.disagree,
    'Strongly Disagree': q.s_disagree,
  }));

  const formatPercent = (value: number) => `${value.toFixed(2)}%`;

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
          <XAxis dataKey="name" angle={-35} textAnchor="end" interval={0} />
          <YAxis tickFormatter={formatPercent} />
          <Tooltip formatter={(value: number) => formatPercent(value)} />
          <Legend verticalAlign="top" />
          <Bar dataKey="Strongly Agree" stackId="a" fill="#22c55e" />
          <Bar dataKey="Agree" stackId="a" fill="#a3e635" />
          <Bar dataKey="Neutral" stackId="a" fill="#facc15" />
          <Bar dataKey="Disagree" stackId="a" fill="#f87171" />
          <Bar dataKey="Strongly Disagree" stackId="a" fill="#ef4444" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function AssessmentList({assessment}:{assessment: AssessmentItem[] | null}) {
  console.log(assessment)
  if (!assessment || assessment.length === 0) {
      return (
        <div className="text-gray-500 italic text-sm">
          No assessment information available.
        </div>
      );
    }
  return (
    <div className="space-y-4">
      {assessment.map((item, idx) => (
        <div
          key={idx}
          className="rounded-xl border border-gray-200 bg-white shadow-md p-4 hover:shadow-lg transition"
        >
          {/* Header: Task + Weight */}
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <ClipboardDocumentListIcon className="w-5 h-5 text-gray-500" />
              {item.task}
            </h3>
            <span className="text-sm font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded-md">
              {item.weight * 100}%
            </span>
          </div>

          {/* Category */}
          <div className="mt-2 flex items-center text-sm text-gray-500 gap-2">
            <TagIcon className="w-4 h-4" />
            {item.category}
          </div>

          {/* Description */}
          {item.description && (
            <p className="mt-3 text-gray-700 text-sm">{item.description}</p>
          )}

          {/* Extra details row */}
          <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-600">
            {item.due_date && (
              <div className="flex items-center gap-1">
                <CalendarIcon className="w-4 h-4" />
                <span>{item.due_date}</span>
              </div>
            )}
            {item.mode && (
              <div className="flex items-center gap-1">
                <BookOpenIcon className="w-4 h-4" />
                <span>{item.mode}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}



function PrereqNode({ prereq, x = 0, y = 0 }: { prereq: Prereq; x?: number; y?: number }) {
  if (prereq.kind === 'atomic') {
    return (
      <g>
        <rect x={x} y={y} width={80} height={40} rx={8} ry={8} fill="#3b82f6" />
        <text x={x + 40} y={y + 25} fill="white" textAnchor="middle" fontSize={12} fontWeight="bold">
          {prereq.value}
        </text>
      </g>
    );
  }

  const spacingX = 100;
  const spacingY = 80;

  return (
    <g>
      {prereq.value.map((child, i) => {
        const childX = x + i * spacingX;
        const childY = y + spacingY;

        return (
          <g key={i}>
            {/* Draw line from parent to child */}
            <line
              x1={x + 40}
              y1={y + 40}
              x2={childX + 40}
              y2={childY}
              stroke="#9ca3af"
              strokeWidth={2}
            />
            {/* Render child node */}
            <PrereqNode prereq={child} x={childX} y={childY} />
          </g>
        );
      })}

      {/* Display AND / OR label at parent node */}
      <rect x={x} y={y} width={80} height={40} rx={8} ry={8} fill="#10b981" />
      <text x={x + 40} y={y + 25} fill="white" textAnchor="middle" fontSize={12} fontWeight="bold">
        {prereq.kind.toUpperCase()}
      </text>
    </g>
  );
}

function PrereqDisplay({ prereq, code }: {prereq: Prereq | null | undefined, code: string}) {
  if (!prereq) return <p>No prereq for this course</p>;
  return (
    <svg width="100%" height="300">
      {/* Main course node */}
      <g>
        <rect x={200} y={20} width={80} height={40} rx={8} ry={8} fill="#f97316" />
        <text x={240} y={45} fill="white"  textAnchor="middle" fontSize={12} fontWeight="bold">
          {code}
        </text>
      </g>

      {/* Render prereq tree below */}
      <PrereqNode prereq={prereq} x={200} y={70} />
    </svg>
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

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, children }: ModalProps) {
  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50">
      <div className="relative bg-white p-6 rounded-lg w-3/4 max-w-3xl max-h-[90vh] overflow-auto shadow-lg">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800 transition-colors"
        >
          Close
        </button>

        {children}
      </div>
    </div>,
    document.body
  );
}


