import { db } from "@/lib/db/client";
import { testExecutions } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDistanceToNow } from "date-fns";
import {
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Github,
  MessageSquare,
  User,
} from "lucide-react";
import Link from "next/link";

export const dynamic = "force-dynamic";

const statusConfig = {
  pending: {
    color: "secondary",
    icon: Clock,
    label: "Pending",
  },
  running: {
    color: "warning",
    icon: Loader2,
    label: "Running",
  },
  passed: {
    color: "success",
    icon: CheckCircle2,
    label: "Passed",
  },
  failed: {
    color: "destructive",
    icon: XCircle,
    label: "Failed",
  },
} as const;

const triggerIcons = {
  slack: MessageSquare,
  github: Github,
  manual: User,
} as const;

export default async function TestExecutionsPage() {
  const executions = await db
    .select()
    .from(testExecutions)
    .orderBy(desc(testExecutions.createdAt));

  return (
    <div className="mx-auto max-w-7xl p-6">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Test Executions</h1>
          <p className="mt-2 text-gray-500">
            View and manage all test execution history
          </p>
        </div>
        <Link href="/test-config">
          <Button>Create New Test</Button>
        </Link>
      </div>

      {executions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Clock className="mb-4 h-12 w-12 text-gray-400" />
            <h3 className="mb-2 text-lg font-semibold">No test executions yet</h3>
            <p className="mb-6 text-sm text-gray-500">
              Create your first test configuration to get started
            </p>
            <Link href="/test-config">
              <Button>Create Test Configuration</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {executions.map((execution) => {
            const config = statusConfig[execution.status];
            const StatusIcon = config.icon;
            const TriggerIcon =
              triggerIcons[execution.triggeredBy as keyof typeof triggerIcons];

            return (
              <Card
                key={execution.id}
                className="transition-shadow hover:shadow-md"
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <StatusIcon
                        className={`h-6 w-6 ${
                          execution.status === "running" ? "animate-spin" : ""
                        } ${
                          execution.status === "passed"
                            ? "text-green-500"
                            : execution.status === "failed"
                            ? "text-red-500"
                            : execution.status === "running"
                            ? "text-yellow-500"
                            : "text-gray-500"
                        }`}
                      />
                      <div>
                        <CardTitle className="text-lg">
                          Test Execution #{execution.id.slice(0, 8)}
                        </CardTitle>
                        <CardDescription className="mt-1 flex items-center gap-2">
                          <TriggerIcon className="h-3 w-3" />
                          <span>
                            Triggered by {execution.triggeredBy}
                            {execution.triggeredByUser &&
                              ` (${execution.triggeredByUser})`}
                          </span>
                          {execution.createdAt && (
                            <>
                              <span>•</span>
                              <span>
                                {formatDistanceToNow(
                                  new Date(execution.createdAt),
                                  {
                                    addSuffix: true,
                                  }
                                )}
                              </span>
                            </>
                          )}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge variant={config.color as any}>{config.label}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* GitHub PR Info */}
                    {execution.githubPrNumber && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Github className="h-4 w-4" />
                        <span>
                          PR #{execution.githubPrNumber}:{" "}
                          {execution.githubPrTitle || "Untitled"}
                        </span>
                      </div>
                    )}

                    {/* Slack Info */}
                    {execution.slackChannelId && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <MessageSquare className="h-4 w-4" />
                        <span>
                          Slack: {execution.slackWorkspace || "Unknown workspace"}
                        </span>
                      </div>
                    )}

                    {/* Execution Time */}
                    {execution.executionTimeMs && (
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">Execution Time:</span>{" "}
                        {(execution.executionTimeMs / 1000).toFixed(2)}s
                      </div>
                    )}

                    {/* Error Message */}
                    {execution.errorDetails && (
                      <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                        <span className="font-medium">Error:</span>{" "}
                        {execution.errorDetails}
                      </div>
                    )}

                    <div className="flex justify-end">
                      <Link href={`/test-executions/${execution.id}`}>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
