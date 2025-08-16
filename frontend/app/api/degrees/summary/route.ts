import { NextResponse } from "next/server"
import { DegreeSummary } from "../types";
import { BACKEND_BASE_URL } from "../../common";

export async function GET() {
    try {
        const res = await fetch(`${BACKEND_BASE_URL}/degrees/summary`)

        if (!res.ok) {
            const errorText = await res.text();
            return NextResponse.json(
                { error: errorText || 'Failed to fetch from external API' },
                { status: res.status }
            );
        }

        const degrees: DegreeSummary[] = await res.json()
        return NextResponse.json(degrees)
    }
    catch (err) {
        console.error(err)
        console.error("Error fetching degree summaries")
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}