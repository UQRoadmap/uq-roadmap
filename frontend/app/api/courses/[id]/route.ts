import { NextResponse } from 'next/server';
import { Course} from '@/types/course'
import MapToCourse from '../types';

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
      const course: Course = MapToCourse(apiCourse)
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
