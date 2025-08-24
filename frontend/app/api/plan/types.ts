import { UUID } from "@/types/common";
import { APIDegreeRead } from "../degree/types";

export interface LucasReadPlan {
    plan_id: UUID
    degree: APIDegreeRead

    name: string
    start_year: number
    end_year: number
    start_sem: 1 | 2
//20251-2 -> 
    // maps (year, sem) -> course_codes e.g., 'CSSE2310'
  course_dates_input: Record<string, string[]>; 
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
  end_year: number;
  start_sem: 1 | 2;

  // maps (year, sem) -> course_codes e.g., 'CSSE2310'
  course_dates_input: Record<string, string[]>; 
  // key is stringified tuple "year,sem"

  // maps (part) -> course_code list
  course_reqs: Record<string, string[]>;

  // maps (part) -> degree code (e.g., "2525")
  specialisations: Record<string, string[]>;
}

export interface JacksonPlan {
    plan_id: UUID
    degree: APIDegreeRead

    name: string
    start_year: number
    end_year: number
    start_sem: 1 | 2
//20251-2 ->  "CSSE2310"
    course_tiles: Record<string, string>; 
  // key is stringified tuple "year,sem" because TS doesn't support tuple as object key

  // maps (part) -> course_code list
  course_reqs: Record<string, string[]>;

  // maps (part) -> degree code (e.g., "2525")
  specialisations: Record<string, string[]>;
}

export function MaptoJacksonPlan(plan: LucasReadPlan): JacksonPlan {
    const result: Record<string, string> = {}
    Object.keys(plan.course_dates_input).forEach(element => {
        const courses: string[] = plan.course_dates_input[element]
        const parts = element.replace("(", "").replace(")", "").split(",").map(v => Number(v))

        const year = parts[0]
        const sem = parts[1]

        let key;
        for (let i = 0; i < courses.length; i++) {
            key = `${year}${sem-1}-${i}`
            if (key in result) {
                console.error(`Duplicate key on ${key}`)
            }
            result[key] = courses[i]
        }
    });

    return {
        plan_id: plan.plan_id,
        degree: plan.degree,
        name: plan.name,
        start_year: plan.start_year,
        start_sem: plan.start_sem,
        end_year: plan.end_year,
        course_tiles: result,
        course_reqs: plan.course_reqs,
        specialisations: plan.specialisations
    }
}

export function MapfromJacksonPlan(plan: JacksonPlan, degree_id: string): APIPlanCreateUpdate {
    const result: Record<string, string[]> = {}
    let lucas_key: string;
    let course: string;
    let year: string
    let sem_num: number
    Object.keys(plan.course_tiles).forEach(pos => {
        course = plan.course_tiles[pos]
        year = pos.substring(0,4)
        sem_num = Number(pos.substring(4,5)) + 1
        lucas_key = `(${year},${sem_num})`
        if (lucas_key in result) {
            result[lucas_key].push(course)
        } else {
            result[lucas_key] = [course]
        }
    });


    return {
        degree_id: degree_id,
        name: plan.name,
        start_year: plan.start_year,
        start_sem: plan.start_sem,
        end_year: plan.end_year,
        course_dates_input: result,
        course_reqs: plan.course_reqs,
        specialisations: plan.specialisations
    }
}
