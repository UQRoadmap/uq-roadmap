import { NextResponse } from 'next/server';
import { Course } from '@/types/course'
import MapToCourse from './types';
import { BACKEND_BASE_URL } from '../common';

export async function GET() {
    try {
        const backendUrl = `${BACKEND_BASE_URL}/course`;

        const res = await fetch(backendUrl);

        if (!res.ok) {
            return NextResponse.json(
                { error: 'Failed to fetch from external API' },
                { status: res.status }
            );
        }

        const apiCourses = await res.json();
        const courses: Course[] = apiCourses.map(MapToCourse);
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
}
