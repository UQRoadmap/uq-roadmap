export interface Plan {
  name: string,
  degree: string,
  percentage: number,
  startYear: number,
  startSem: number
  endYear: number,
  id: string,
  courses: PlannedCourses,
}

export interface PlannedCourses {
  [year: string]: {
    sem: CourseData[];
  }
};

export interface CourseData {
  code: string,
  pos: number,
}
