import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db/client";
import { testExecutions } from "@/lib/db/schema";
import { desc } from "drizzle-orm";

export async function GET() {
  try {
    const executions = await db
      .select()
      .from(testExecutions)
      .orderBy(desc(testExecutions.createdAt));

    return NextResponse.json({ executions });
  } catch (error) {
    console.error("Error fetching test executions:", error);
    return NextResponse.json(
      { error: "Failed to fetch test executions" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const [newExecution] = await db
      .insert(testExecutions)
      .values(body)
      .returning();

    return NextResponse.json({ execution: newExecution }, { status: 201 });
  } catch (error) {
    console.error("Error creating test execution:", error);
    return NextResponse.json(
      { error: "Failed to create test execution" },
      { status: 500 }
    );
  }
}
