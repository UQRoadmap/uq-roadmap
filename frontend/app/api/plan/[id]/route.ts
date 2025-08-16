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
    id: "123"
}];

export async function GET(request: Request, { params }: { params: { id: string } }) {
  const { id } = params;
  console.log('GET /api/plan/[id]', { id });

  const plan = data.find(value => value.id === id);
  if (!plan) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  return NextResponse.json(plan);
}

export async function POST(request: Request) {
  // return all plans or handle body as needed
  return NextResponse.json(data);
}