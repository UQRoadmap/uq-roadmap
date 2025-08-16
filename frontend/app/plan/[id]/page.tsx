import { notFound } from 'next/navigation';
import { PlanDetailClient } from './planDetails';
import { Plan } from '@/types/plan';

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


export default async function PlanPage(params: { params: Promise<{ id: string }> }) {
    const { id } = await params.params;
    const plan = await getPlan(id);

    if (!plan) {
        notFound();
    }

    return <PlanDetailClient plan={plan} />;
}