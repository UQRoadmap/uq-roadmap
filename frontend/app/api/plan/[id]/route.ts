import { NextRequest, NextResponse } from "next/server"
import { APIPlanCreateUpdate, LucasReadPlan, MaptoJacksonPlan } from "../types";
import { BACKEND_BASE_URL } from "../../common";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;

    try {
        const res = await fetch(`${BACKEND_BASE_URL}/plan/${id}`);
        if (res.status == 404) {
            console.debug(`Couldn't find plan under id: ${id}`)
            return NextResponse.json(null)
        }
        if (!res.ok) {
            const errorText = await res.text();
            return NextResponse.json(
                { error: errorText || `Failed to fetch plan ${id}` },
                { status: res.status }
            );
        }
        const plan: LucasReadPlan = await res.json();
        const mapped = MaptoJacksonPlan(plan);
        console.log(`Just got jackson plan: ${JSON.stringify(mapped)}`)
        return NextResponse.json(mapped);
    } catch (err) {
        console.error(err);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}

export async function PUT(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;

    try {
        const body: APIPlanCreateUpdate = await req.json();
        const res = await fetch(`${BACKEND_BASE_URL}/plan/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const errorText = await res.text();
            return NextResponse.json(
                { error: errorText || `Failed to update plan ${id}` },
                { status: res.status }
            );
        }

        const plan: LucasReadPlan = await res.json();
        const mapped = MaptoJacksonPlan(plan);
        console.log(`Just got jackson plan: ${JSON.stringify(mapped)}`)
        return NextResponse.json(mapped);
    } catch (err) {
        console.error(err);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}