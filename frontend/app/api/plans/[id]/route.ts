import { NextResponse } from "next/server"
import { APIPlanCreateUpdate, APIPlanRead} from "../types";
import { BACKEND_BASE_URL } from "../../common";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const {id} = await params;

  try {
    const res = await fetch(`${BACKEND_BASE_URL}/plans/${id}`);
    if (!res.ok) {
      return NextResponse.json(
        { error: `Failed to fetch plan ${id}` },
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

export async function PUT(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    const body: APIPlanCreateUpdate = await req.json();
    const res = await fetch(`${BACKEND_BASE_URL}/plans/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Failed to update plan ${id}` },
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