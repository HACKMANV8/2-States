import { db } from "@/lib/db/client";
import { testExecutions, configurationTemplates } from "@/lib/db/schema";
import { eq } from "drizzle-orm";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDistanceToNow, format } from "date-fns";
import {
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Github,
  MessageSquare,
  User,
  ArrowLeft,
  Monitor,
  Wifi,
  Smartphone,
  PlayCircle,
} from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

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

export default async function TestExecutionDetailPage({
  params,
}: {
  params: Promise<{ executionId: string }>;
}) {
  const { executionId } = await params;

  const [execution] = await db
    .select()
    .from(testExecutions)
    .where(eq(testExecutions.id, executionId))
    .limit(1);

  if (!execution) {
    notFound();
  }

  // Fetch related config if exists
  let config = null;
  if (execution.configId) {
    [config] = await db
      .select()
      .from(configurationTemplates)
      .where(eq(configurationTemplates.id, execution.configId))
      .limit(1);
  }

  const statusCfg = statusConfig[execution.status];
  const StatusIcon = statusCfg.icon;

  return (
    <div className="mx-auto max-w-7xl p-6">
      {/* Header */}
      <div className="mb-8">
        <Link href="/test-executions">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Test Executions
          </Button>
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Test Execution #{execution.id.slice(0, 8)}
            </h1>
            <p className="mt-2 text-gray-500">
              Detailed test execution report and logs
            </p>
          </div>
          <div className="flex items-center gap-3">
            {execution.testSuiteId && (
              <Link href={`/test-library/${execution.testSuiteId}/run`}>
                <Button variant="outline">
                  <PlayCircle className="mr-2 h-4 w-4" />
                  Re-run Test
                </Button>
              </Link>
            )}
            <Badge variant={statusCfg.color as any} className="text-base">
              <StatusIcon
                className={`mr-2 h-5 w-5 ${
                  execution.status === "running" ? "animate-spin" : ""
                }`}
              />
              {statusCfg.label}
            </Badge>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="space-y-6 lg:col-span-2">
          {/* Execution Details */}
          <Card>
            <CardHeader>
              <CardTitle>Execution Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Triggered By
                  </span>
                  <div className="mt-1 flex items-center gap-2">
                    {execution.triggeredBy === "slack" && (
                      <MessageSquare className="h-4 w-4" />
                    )}
                    {execution.triggeredBy === "github" && (
                      <Github className="h-4 w-4" />
                    )}
                    {execution.triggeredBy === "manual" && (
                      <User className="h-4 w-4" />
                    )}
                    <span className="capitalize">{execution.triggeredBy}</span>
                    {execution.triggeredByUser && (
                      <span className="text-gray-500">
                        ({execution.triggeredByUser})
                      </span>
                    )}
                  </div>
                </div>

                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Started At
                  </span>
                  <div className="mt-1">
                    {execution.startedAt
                      ? format(new Date(execution.startedAt), "PPpp")
                      : "Not started"}
                  </div>
                </div>

                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Completed At
                  </span>
                  <div className="mt-1">
                    {execution.completedAt
                      ? format(new Date(execution.completedAt), "PPpp")
                      : execution.status === "running"
                      ? "In progress..."
                      : "Not completed"}
                  </div>
                </div>

                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Execution Time
                  </span>
                  <div className="mt-1">
                    {execution.executionTimeMs
                      ? `${(execution.executionTimeMs / 1000).toFixed(2)}s`
                      : "N/A"}
                  </div>
                </div>
              </div>

              {/* GitHub PR Info */}
              {execution.githubPrNumber && (
                <div className="rounded-lg border bg-gray-50 p-4">
                  <div className="flex items-start gap-3">
                    <Github className="h-5 w-5 text-gray-600" />
                    <div className="flex-1">
                      <div className="font-medium">
                        Pull Request #{execution.githubPrNumber}
                      </div>
                      {execution.githubPrTitle && (
                        <div className="mt-1 text-sm text-gray-600">
                          {execution.githubPrTitle}
                        </div>
                      )}
                      {execution.githubRepoUrl && (
                        <div className="mt-1 text-sm text-gray-500">
                          {execution.githubRepoUrl}
                        </div>
                      )}
                      {execution.githubCommitSha && (
                        <div className="mt-1 font-mono text-xs text-gray-500">
                          {execution.githubCommitSha.slice(0, 7)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Slack Info */}
              {execution.slackChannelId && (
                <div className="rounded-lg border bg-gray-50 p-4">
                  <div className="flex items-start gap-3">
                    <MessageSquare className="h-5 w-5 text-gray-600" />
                    <div className="flex-1">
                      <div className="font-medium">Slack Integration</div>
                      {execution.slackWorkspace && (
                        <div className="mt-1 text-sm text-gray-600">
                          Workspace: {execution.slackWorkspace}
                        </div>
                      )}
                      <div className="mt-1 text-sm text-gray-500">
                        Channel ID: {execution.slackChannelId}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Error Display */}
          {execution.errorDetails && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="text-red-900">Error Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-red-900">
                    Error Message:
                  </span>
                  <div className="mt-1 rounded bg-red-100 p-3 font-mono text-sm text-red-900">
                    {execution.errorDetails}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Execution Logs */}
          {execution.executionLogs && (
            <Card>
              <CardHeader>
                <CardTitle>Test Logs</CardTitle>
                <CardDescription>Test execution logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-96 overflow-auto rounded-lg bg-gray-900 p-4 font-mono text-sm text-green-400">
                  <pre className="whitespace-pre-wrap">
                    {typeof execution.executionLogs === 'string'
                      ? execution.executionLogs
                      : JSON.stringify(execution.executionLogs, null, 2)}
                  </pre>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Test Configuration */}
          {config && (
            <Card>
              <CardHeader>
                <CardTitle>Test Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Name</div>
                  <div className="mt-1">{config.name}</div>
                </div>
                {config.description && (
                  <div>
                    <div className="text-sm font-medium text-gray-500">
                      Description
                    </div>
                    <div className="mt-1 text-sm">{config.description}</div>
                  </div>
                )}
                {config.browsers && (
                  <div>
                    <div className="text-sm font-medium text-gray-500">
                      Browsers
                    </div>
                    <div className="mt-1 text-sm">
                      {JSON.parse(config.browsers).join(", ")}
                    </div>
                  </div>
                )}
                {config.networkModes && (
                  <div>
                    <div className="text-sm font-medium text-gray-500">
                      Network Modes
                    </div>
                    <div className="mt-1 text-sm">
                      {JSON.parse(config.networkModes).join(", ")}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Screenshots */}
          {execution.screenshots && (
            <Card>
              <CardHeader>
                <CardTitle>Screenshots</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-gray-600">
                  {(() => {
                    try {
                      const parsed = typeof execution.screenshots === 'string'
                        ? JSON.parse(execution.screenshots)
                        : execution.screenshots;
                      return `${Array.isArray(parsed) ? parsed.length : 0} screenshot(s) captured`;
                    } catch {
                      return "Screenshots available";
                    }
                  })()}
                </div>
                {/* TODO: Display screenshots */}
              </CardContent>
            </Card>
          )}

          {/* Video URL */}
          {execution.videoUrl && (
            <Card>
              <CardHeader>
                <CardTitle>Video Recording</CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href={execution.videoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline text-sm"
                >
                  View Recording
                </a>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
