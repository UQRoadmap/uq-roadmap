import Image from "next/image"
import IconImage from "@/public/logo.png"

export default function Logo() {
   return (
        <div className="-m-1.5 p-1.5 text-white font-black flex items-center justify-center">
            <Icon height={64} width={64}/>
            <span className="text-lg leading-none flex">
                <div className='mr-1'>UQ</div>RoadMap
            </span>
        </div>
    )
}

export function Icon({height, width, className}: {height: number, width: number, className?: string}) {
    return(
        <Image src={IconImage} height={height} width={width} alt="Graduation Cap" className={className} />
    )
}