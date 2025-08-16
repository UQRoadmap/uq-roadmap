import { UUID } from "@/types/common";
import { APIDegreeRead } from "../degrees/types";

export interface APIPlanRead {
    plan_id: UUID
    degree: APIDegreeRead

    name: string
    start_year: number
    start_sem: 1 | 2
    end_year?: number

    // maps (year, sem) -> course_codes e.g., 'CSSE2310'
    course_dates: Record<string, string[]>; 
  // key is stringified tuple "year,sem" because TS doesn't support tuple as object key

  // maps (part) -> course_code list
  course_reqs: Record<string, string[]>;

  // maps (part) -> degree code (e.g., "2525")
  specialisations: Record<string, string[]>;

  courses: string[];
}

export interface APIPlanCreateUpdate {
  degree_id: string; // UUID as string
  name: string;

  start_year: number;
  start_sem: 1 | 2;
  end_year?: number;

  // maps (year, sem) -> course_codes e.g., 'CSSE2310'
  course_dates: Record<string, string[]>; 
  // key is stringified tuple "year,sem"

  // maps (part) -> course_code list
  course_reqs: Record<string, string[]>;

  // maps (part) -> degree code (e.g., "2525")
  specialisations: Record<string, string[]>;
}