export type Course = {
  id: string;
  code: string;
  name: string;

  units: number;
  sem: string;
  sems: string[];
  secats: number,
  desc: string,

  degreeReq: DegreeReq;
  completed: boolean;
};

export type DegreeReq = Record<string, string[]>;

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
