import { TestStatusCard } from "@/components/dashboard/test-status-card";
import { RecentExecutions } from "@/components/dashboard/recent-executions";
import {
  PlayCircle,
  CheckCircle2,
  XCircle,
  Clock,
  Github,
  MessageSquare,
} from "lucide-react";
import { db } from "@/lib/db/client";
import { testExecutions } from "@/lib/db/schema";
import { desc, eq, and, count } from "drizzle-orm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  // Fetch test execution statistics
  const allExecutions = await db
    .select()
    .from(testExecutions)
    .orderBy(desc(testExecutions.createdAt));

  const recentExecutions = allExecutions.slice(0, 5);

  // Calculate stats
  const totalTests = allExecutions.length;
  const passedTests = allExecutions.filter((e) => e.status === "passed").length;
  const failedTests = allExecutions.filter((e) => e.status === "failed").length;
  const runningTests = allExecutions.filter(
    (e) => e.status === "running"
  ).length;

  return (
    <div className="mx-auto max-w-7xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Test Dashboard</h1>
        <p className="mt-2 text-gray-500">
          Monitor and manage your automated testing with TestGPT
        </p>
      </div>

      {/* Status Cards */}
      <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <TestStatusCard
          title="Total Tests"
          value={totalTests}
          icon={PlayCircle}
          description="All test executions"
          iconColor="text-blue-500"
        />
        <TestStatusCard
          title="Passed"
          value={passedTests}
          icon={CheckCircle2}
          description="Successful tests"
          iconColor="text-green-500"
        />
        <TestStatusCard
          title="Failed"
          value={failedTests}
          icon={XCircle}
          description="Failed tests"
          iconColor="text-red-500"
        />
        <TestStatusCard
          title="Running"
          value={runningTests}
          icon={Clock}
          description="Currently executing"
          iconColor="text-yellow-500"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Executions */}
        <div className="lg:col-span-2">
          <RecentExecutions executions={recentExecutions} />
        </div>

        {/* Quick Actions */}
        <Card className="h-fit">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link href="/test-config" className="block">
              <Button className="w-full" variant="outline" size="sm">
                <PlayCircle className="mr-2 h-4 w-4" />
                Create New Test
              </Button>
            </Link>
            <Link href="/test-library" className="block">
              <Button className="w-full" variant="outline" size="sm">
                <Clock className="mr-2 h-4 w-4" />
                View Test Library
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
