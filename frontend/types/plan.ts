export interface Plan {
  name: string,
  id: string,
  degree: Degree,

  percentage: number,

  start_sem: number
  end_year: number,

  courses: PlannedCourses,

  specialisations: object,
}

export interface PlannedCourses {
  [year: string]: {
    sem: CourseData[];
  }
};

export interface CourseData {
  code: string,
  pos: number,
  part_id: string
}

export interface Degree {
  degree_id: string,
  degree_code: number,
  year: number,
  title: string,
  degree_url: string,
}
