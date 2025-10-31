import { db } from "@/lib/db/client";
import { testExecutions, testConfigurations } from "@/lib/db/schema";
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
      .from(testConfigurations)
      .where(eq(testConfigurations.id, execution.configId))
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
          {execution.errorMessage && (
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
                    {execution.errorMessage}
                  </div>
                </div>
                {execution.errorStack && (
                  <div>
                    <span className="text-sm font-medium text-red-900">
                      Stack Trace:
                    </span>
                    <div className="mt-1 max-h-64 overflow-auto rounded bg-red-100 p-3 font-mono text-xs text-red-900">
                      {execution.errorStack}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Playwright Output */}
          {execution.playwrightOutput && (
            <Card>
              <CardHeader>
                <CardTitle>Test Logs</CardTitle>
                <CardDescription>Playwright execution output</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-96 overflow-auto rounded-lg bg-gray-900 p-4 font-mono text-sm text-green-400">
                  <pre className="whitespace-pre-wrap">
                    {execution.playwrightOutput}
                  </pre>
                </div>
              </CardContent>
            </Card>
          )}

          {/* AI Generated Tests */}
          {execution.aiGeneratedTests && (
            <Card>
              <CardHeader>
                <CardTitle>AI Generated Test Code</CardTitle>
                <CardDescription>
                  Tests generated by TestGPT for re-running
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-96 overflow-auto rounded-lg bg-gray-900 p-4 font-mono text-sm text-blue-300">
                  <pre className="whitespace-pre-wrap">
                    {execution.aiGeneratedTests}
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
                <div>
                  <div className="text-sm font-medium text-gray-500">
                    Test Prompt
                  </div>
                  <div className="mt-1 rounded bg-gray-50 p-3 text-sm">
                    {config.prompt}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Device & Network Info */}
          {config && (
            <Card>
              <CardHeader>
                <CardTitle>Configuration Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Wifi className="h-4 w-4 text-gray-500" />
                  <div>
                    <div className="text-sm font-medium">Network Mode</div>
                    <div className="text-sm text-gray-600 capitalize">
                      {config.networkMode}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {config.deviceType === "desktop" ? (
                    <Monitor className="h-4 w-4 text-gray-500" />
                  ) : (
                    <Smartphone className="h-4 w-4 text-gray-500" />
                  )}
                  <div>
                    <div className="text-sm font-medium">Device</div>
                    <div className="text-sm text-gray-600 capitalize">
                      {config.deviceType}
                      {config.deviceVersion && ` - ${config.deviceVersion}`}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Monitor className="h-4 w-4 text-gray-500" />
                  <div>
                    <div className="text-sm font-medium">Screen Size</div>
                    <div className="text-sm text-gray-600">
                      {config.screenWidth} x {config.screenHeight}
                      {config.aspectRatio && ` (${config.aspectRatio})`}
                    </div>
                  </div>
                </div>

                {config.featureFlags && (
                  <div>
                    <div className="text-sm font-medium text-gray-500">
                      Feature Flags
                    </div>
                    <div className="mt-1 rounded bg-gray-50 p-2 font-mono text-xs">
                      {config.featureFlags}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Network Simulation Results */}
          {execution.networkSimulationResults && (
            <Card>
              <CardHeader>
                <CardTitle>Network Simulation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded bg-gray-50 p-3 font-mono text-xs">
                  {execution.networkSimulationResults}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Screenshots */}
          {execution.screenshotUrls && (
            <Card>
              <CardHeader>
                <CardTitle>Screenshots</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-gray-600">
                  {JSON.parse(execution.screenshotUrls).length} screenshot(s)
                  captured
                </div>
                {/* TODO: Display screenshots */}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
