export type Course = {
  id: string;
  code: string;
  name: string;

  units: number;
  sem: string;
  sems: string[];
  secats: number,
  desc: string,

  degreeReq: DegreeReq,
  completed: boolean,
  assessment?: AssessmentItem[]
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
