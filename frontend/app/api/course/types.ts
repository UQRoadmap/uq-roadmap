import { Course} from '@/types/course'

export type ApiCourse = {
    course_id: string,
    category: string,
    code: string,
    name: string,
    description: string,
    level: string,
    num_units: number,
    attendance_mode: string,
    active: boolean,
    semesters_str: string,
    score?: number
    secat: {
      num_enrolled: number,
      num_responses: number,
      response_rate: number,
      questions: [
        {
          name: string,
          s_agree: number,
          agree: number,
          middle: number,
          disagree: number,
          s_disagree: number,
        },
      ],
    },
    assessment: {
      items: [
        {
          task: string,
          category: string,
          description: string,
          weight: number,
          due_date: string,
          mode: string,
          learning_outcomes: string[],
          hurdle: boolean,
          identity_verified: boolean,
        },
      ],
    },
    full_code: string,
    semesters: string[],
}


export default function MapToCourse(apiCourse: ApiCourse): Course {
  return {
    id: apiCourse.course_id,
    code: apiCourse.full_code,
    name: apiCourse.name,

    units: apiCourse.num_units,
    sem: "filler",
    sems: apiCourse.semesters,
    secats: apiCourse.score ?? 0,
    desc: apiCourse.description,

    degreeReq: { filler: ["filler"] },
    completed: false,
    assessment?: apiCourse.assessment,
  };
}
