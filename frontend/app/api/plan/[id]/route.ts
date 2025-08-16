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
export async function POST(request: Request) {
  // return all plans or handle body as needed
  console.log(request);
  const body = await request.json();
  console.log(body);
  return NextResponse.json(body.id);
}
