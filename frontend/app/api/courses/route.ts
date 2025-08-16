import { NextResponse } from 'next/server';
import { Course, ApiCourse } from '@/types/course'

function mapToCourse(apiCourse: ApiCourse): Course {
  return {
    id: apiCourse.course_id,
    code: apiCourse.code,
    name: apiCourse.name,

    units: apiCourse.num_units,
    sem: "filler",
    sems: apiCourse.semesters,
    secats: 3.2,
    desc: apiCourse.description,

    degreeReq: { filler: ["filler"] },
    completed: false,
  };
}

export async function GET(
  request: Request,
) {
  try {
      const res = await fetch('http://localhost:8080/courses');

      if (!res.ok) {
        return NextResponse.json(
          { error: 'Failed to fetch from external API' },
          { status: res.status }
        );
      }

      const apiCourses = await res.json();
      const courses: Course[] = apiCourses.map(mapToCourse);
      console.log(courses)
      if (!courses || courses.length === 0) {
        return NextResponse.json({ error: 'No courses found' }, { status: 404 });
      }

      return NextResponse.json(courses);
    } catch (err) {
      console.error('Error fetching courses:', err);
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    }
}
