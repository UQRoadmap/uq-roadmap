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
  assessment: AssessmentItem[] | null,
  secat: Secat | null,
  prereq: object | null,
};

export type Secat = {
  num_enrolled: number;
  num_responses: number;
  response_rate: number;
  questions: {
    name: string;
    s_agree: number;
    agree: number;
    middle: number;
    disagree: number;
    s_disagree: number;
  }[];
};

export type AssessmentItem = {
  task: string;
  category: string;
  description: string;
  weight: number;
  due_date: string;
  mode: string;
  learning_outcomes: string[];
  hurdle: boolean;
  identity_verified: boolean;
};

export type DegreeReq = Record<string, string[]>;
