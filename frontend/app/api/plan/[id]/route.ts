import { Plan } from '@/types/plan';
import { NextResponse } from 'next/server';

const data = [{
    name: "My Plan",
    degree: "Bachelor Engineering (Honours) and Master of Engineering",
    percentage: 29,
    plannedCompleteSem: "20252",
    unitsRemaining: 8,
    startYear: 2024,
    endYear: 2026,
    id: "123",
    major: ["Design"],
    minor: ["Data Science"],
    programReqs: ["Core Courses", "Electives"]
}];

export async function GET(
  request: Request,
  params: { params: Promise<{ id: string }> }
) {
      const res = await fetch(`http://localhost:8080/plans/${id}`);

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
  const { id } = await params.params

  const plan = data.find(value => value.id === id);
  if (!plan) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  return NextResponse.json(plan);
}

export async function POST(request: Request) {
  // return all plans or handle body as needed
  console.log(request);
  const body = await request.json();
  console.log(body);
  return NextResponse.json(body.id);
}
