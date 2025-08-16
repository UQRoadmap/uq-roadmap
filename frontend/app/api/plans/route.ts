import { NextResponse } from "next/server"
import { BACKEND_BASE_URL } from "../common";
import { APIPlanCreateUpdate, APIPlanRead } from "./types";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/plans`);
    if (!res.ok) {
        console.error(res)
      return NextResponse.json(
        { error: "Failed to fetch plans" },
        { status: res.status }
      );
    }

    const plans: APIPlanRead[] = await res.json();
    return NextResponse.json(plans);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body: APIPlanCreateUpdate= await req.json();
    const res = await fetch(`${BACKEND_BASE_URL}/plans`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: "Failed to create plan" },
        { status: res.status }
      );
    }

    const plan: APIPlanRead = await res.json();
    return NextResponse.json(plan);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}