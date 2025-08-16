import { UUID } from "@/types/common"

export interface DegreeSummary {
    title: string
    degree_code: string
    years: number[]
}

export interface APIDegreeRead {
    degree_id: UUID
    degree_code: string
    year: number
    title: string
    degree_url: string | null
}