import { NextRequest, NextResponse } from 'next/server';
import { DetailedCourse } from '@/types/course'
import { MapToDetailedCourse }  from '../types';
import { BACKEND_BASE_URL } from '../../common';

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    try {
        const { id } = await params

        const backendUrl = `${BACKEND_BASE_URL}/course/${id}`;
        const res = await fetch(backendUrl);

        if (!res.ok) {
            return NextResponse.json(
                { error: 'Failed to fetch from external API' },
                { status: res.status }
            );
        }
        const apiCourse = await res.json();
        const course: DetailedCourse = MapToDetailedCourse(apiCourse)
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
