import { notFound } from 'next/navigation';
import { PlanDetailClient } from './planDetails';
import { Course } from '@/types/course';
import { JacksonPlan } from '@/app/api/plan/types';

async function getPlan(id: string): Promise<JacksonPlan | null> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";
    const res = await fetch(`${baseUrl}/plan/${id}`);
    if (!res.ok) {
        if (res.status === 404) {
            console.debug(`plan not found under id '${id}'`)
            return null;
        }
        throw new Error('Failed to fetch plan');
    }
    return res.json();
}

async function getCourses(): Promise<Course[] | null> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";
    const res = await fetch(`${baseUrl}/course`);
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
    const plan = await getPlan(id);
    if (!plan || !courses) {
        notFound();
    }

    return (<PlanDetailClient initialPlan={plan} courses={courses}/>);
}
