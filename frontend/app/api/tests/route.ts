import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db/client";
import { testConfigurations } from "@/lib/db/schema";

export async function GET() {
  try {
    const configs = await db.select().from(testConfigurations);
    return NextResponse.json({ configs });
  } catch (error) {
    console.error("Error fetching test configurations:", error);
    return NextResponse.json(
      { error: "Failed to fetch test configurations" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const [newConfig] = await db
      .insert(testConfigurations)
      .values(body)
      .returning();

    return NextResponse.json({ config: newConfig }, { status: 201 });
  } catch (error) {
    console.error("Error creating test configuration:", error);
    return NextResponse.json(
      { error: "Failed to create test configuration" },
      { status: 500 }
    );
  }
}
