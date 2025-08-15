import { EllipsisVerticalIcon, StarIcon, PlusIcon } from "@heroicons/react/20/solid";

export default function CourseCard({name, id, units, degreeReq}: {name: string, id: string, units: number, degreeReq: string}) {
    return (
        <div
            className="box-border h-30 flex flex-col justify-between rounded-lg border border-gray-400 shadow-md overflow-hidden"
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
                <div className="truncate">{id}</div>
                <div>
                    {units} Units
                </div>
                <div className="flex items-center space-x-1 text-yellow-400">
                    <span>4.77</span>
                    <StarIcon className="w-3 h-3" />
                </div>
            </div>
            <div className="text-xs mt-2 truncate flex justify-between w-full" title={degreeReq}>
            </div>
        </div>
    )
}

export function EmptyCourseCard({degreeReq}: {degreeReq?: string}) {
    return (
        <div
            className="relative box-border h-30 flex flex-col justify-between rounded-lg border border-dashed border-gray-400 shadow-md overflow-hidden"
        >
            {/* Overlay to dim entire card with interactive icon */}
            <div className="absolute inset-0 bg-gray-800/50 z-10 rounded-lg flex items-center justify-center">
                <PlusIcon className="h-6 w-6 text-white" />
            </div>
            <div className="bg-red-400 p-2 space-y-1 flex justify-between align-center h-9">
                <div className="text-xs font-medium truncate">
                    {degreeReq ?? "Elective"}
                </div>
                <div>

                </div>
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