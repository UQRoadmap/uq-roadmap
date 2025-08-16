import { NextResponse } from "next/server"
import { BACKEND_BASE_URL } from "../common";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const degree_code = searchParams.get("degree_code");
    const year = searchParams.get("year");

    if (!degree_code || !year) {
      return NextResponse.json(
        { error: "Missing required query params: degree_code, year" },
        { status: 400 }
      );
    }

    const backendUrl = `${BACKEND_BASE_URL}/degrees/simple?degree_code=${degree_code}&year=${year}`;
    const res = await fetch(backendUrl);

    if (!res.ok) {
      return NextResponse.json(
        { error: "Failed to fetch degree" },
        { status: res.status }
      );
    }

    const degree = await res.json();
    return NextResponse.json(degree);
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}