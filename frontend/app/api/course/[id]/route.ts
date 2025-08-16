import { NextResponse } from 'next/server';
import { Course } from '@/types/course'
import MapToCourse from '../types';
import { BACKEND_BASE_URL } from '../../common';

export async function GET({ params }: { params: { id: string } }) {
    try {
        const { id } = params

        const backendUrl = `${BACKEND_BASE_URL}/course/${id}`;
        const res = await fetch(backendUrl);

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
