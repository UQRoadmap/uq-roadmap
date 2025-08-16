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
  { params }: { params: { id: string } }
) {
  try {
      const { id } = params
      const res = await fetch(`http://localhost:8080/courses/${id}`);

      if (!res.ok) {
        return NextResponse.json(
          { error: 'Failed to fetch from external API' },
          { status: res.status }
        );
      }
      const apiCourse = await res.json();
      const course: Course = mapToCourse(apiCourse)
      console.log(course)
      if (!course) {
        return NextResponse.json({ error: `No course found with ${id}` }, { status: 404 });
      }

      return NextResponse.json(course);
    } catch (err) {
      console.error('Error fetching course:', err);
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    }
}
