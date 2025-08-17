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
