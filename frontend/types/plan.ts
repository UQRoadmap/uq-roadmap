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

export type CourseData = [string, number] // [courseCode, grid_pos]
