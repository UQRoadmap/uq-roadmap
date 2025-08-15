import { EllipsisVerticalIcon, StarIcon } from "@heroicons/react/16/solid";


// Course card component
export default function CourseCard({name, id, units, degreeReq}: {name: string, id: string, units: number, degreeReq: string}) {
    return (
        <div
            className="box-border min-h-[6rem] flex flex-col justify-between rounded-lg border border-gray-400 shadow-md overflow-hidden"
            key={id}
        >
            <div className="bg-red-400 p-2 space-y-1 flex justify-between align-center">
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