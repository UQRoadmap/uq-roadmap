import { notFound } from 'next/navigation';
import { PlanDetailClient } from './planDetails';
import { Plan } from '@/types/plan';
import { Course } from '@/types/course';

async function getPlan(id: string): Promise<Plan | null> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";
    const res = await fetch(`${baseUrl}/plan/${id}`);
    if (!res.ok) {
        if (res.status === 404) {
            return null;
        }
        throw new Error('Failed to fetch plan');
    }
    return res.json();
}

async function getCourses(): Promise<Course[] | null> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";
    const res = await fetch(`${baseUrl}/courses`);
    if (!res.ok) {
        if (res.status === 404) {
            return null;
        }
        console.log(res)
        throw new Error('Failed to fetch courses'  + res.status);
    }
    return res.json();
}


export default async function PlanPage(params: { params: Promise<{ id: string }> }) {
    const { id } = await params.params;
    const courses = await getCourses();
    console.log(courses)
    const plan = await getPlan(id);
    console.log(plan)
    if (!plan) {
        notFound();
    }

    return <PlanDetailClient plan={plan} courses={courses}/>;
}
