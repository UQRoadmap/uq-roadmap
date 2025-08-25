import { NextResponse } from "next/server"
import { BACKEND_BASE_URL } from "../common";
import { APIPlanCreateUpdate } from "./types";
import { Plan } from "@/types/plan";

export async function GET() {
    try {
        const res = await fetch(`${BACKEND_BASE_URL}/plan`);
        if (!res.ok) {
            console.error(res)

            const errorText = await res.text();
            return NextResponse.json(
                { error: errorText || "Failed to fetch plans" },
                { status: res.status }
            );
        }

        const plans: Plan[] = await res.json();
        console.log(plans)
        return NextResponse.json(plans);
    } catch (err) {
        console.error(err);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}

export async function POST(req: Request) {
    try {
        const body: APIPlanCreateUpdate = await req.json();
        const res = await fetch(`${BACKEND_BASE_URL}/plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!res.ok) {

            const errorText = await res.text();
            return NextResponse.json(
                { error: errorText || "Failed to create plan" },
                { status: res.status }
            );
        }

        const plan: Plan = await res.json();
        return plan
    } catch (err) {
        console.error(err);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}
