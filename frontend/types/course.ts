export type Course = {
  id: string;
  name: string;

  units: number;
  sem: string;
  secats: number,
  desc: string,

  degreeReq?: string;
  completed: boolean;
};
