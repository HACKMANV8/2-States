import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import {
  PlayCircle,
  ArrowLeft,
  Globe,
  Calendar,
  User,
  Tag,
  CheckCircle2,
  XCircle,
  Clock as ClockIcon,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

async function getTestSuite(testId: string) {
  try {
    return await apiClient.getTestSuite(testId);
  } catch (error) {
    return null;
  }
}

async function getTestHistory(testId: string) {
  try {
    return await apiClient.getTestHistory(testId, 10);
  } catch (error) {
    return null;
  }
}

export default async function TestDetailPage({
  params,
}: {
  params: { testId: string };
}) {
  const [testSuite, history] = await Promise.all([
    getTestSuite(params.testId),
    getTestHistory(params.testId),
  ]);

  if (!testSuite) {
    notFound();
  }

  return (
    <div className="mx-auto max-w-7xl p-6">
      {/* Header */}
      <div className="mb-6">
        <Link href="/test-library">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Library
          </Button>
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{testSuite.name}</h1>
            {testSuite.description && (
              <p className="mt-2 text-gray-600">{testSuite.description}</p>
            )}
          </div>
          <Link href={`/test-library/${params.testId}/run`}>
            <Button size="lg">
              <PlayCircle className="mr-2 h-5 w-5" />
              Run Test
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Test Details */}
          <Card>
            <CardHeader>
              <CardTitle>Test Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-sm">
                <Globe className="h-4 w-4 text-gray-500" />
                <span className="font-medium">Target URL:</span>
                <a
                  href={testSuite.target_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {testSuite.target_url}
                </a>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span className="font-medium">Created:</span>
                <span>
                  {formatDistanceToNow(new Date(testSuite.created_at), {
                    addSuffix: true,
                  })}
                </span>
              </div>

              {testSuite.created_by && (
                <div className="flex items-center gap-2 text-sm">
                  <User className="h-4 w-4 text-gray-500" />
                  <span className="font-medium">Created by:</span>
                  <span>{testSuite.created_by}</span>
                </div>
              )}

              {testSuite.tags && testSuite.tags.length > 0 && (
                <div className="flex items-start gap-2 text-sm">
                  <Tag className="h-4 w-4 text-gray-500 mt-0.5" />
                  <span className="font-medium">Tags:</span>
                  <div className="flex flex-wrap gap-1">
                    {testSuite.tags.map((tag) => (
                      <Badge key={tag} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Test Steps */}
          <Card>
            <CardHeader>
              <CardTitle>Test Steps</CardTitle>
              <CardDescription>
                {testSuite.test_steps.length} step(s) configured
              </CardDescription>
            </CardHeader>
            <CardContent>
              {testSuite.test_steps.length === 0 ? (
                <p className="text-sm text-gray-500">
                  No test steps defined yet
                </p>
              ) : (
                <div className="space-y-3">
                  {testSuite.test_steps.map((step, index) => (
                    <div
                      key={index}
                      className="rounded-lg border border-gray-200 p-3"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                          {step.step_number}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {step.action}
                            </Badge>
                            <span className="text-sm font-medium">
                              {step.target}
                            </span>
                          </div>
                          <p className="mt-1 text-sm text-gray-600">
                            {step.expected_outcome}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Statistics */}
          {history && (
            <Card>
              <CardHeader>
                <CardTitle>Test Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-2xl font-bold">{history.total_runs}</div>
                  <div className="text-sm text-gray-500">Total Runs</div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span>Passed</span>
                  </div>
                  <div className="font-semibold">{history.passed_runs}</div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span>Failed</span>
                  </div>
                  <div className="font-semibold">{history.failed_runs}</div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Executions */}
          {history && history.executions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Executions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {history.executions.slice(0, 5).map((execution) => (
                    <Link
                      key={execution.id}
                      href={`/test-executions/${execution.id}`}
                    >
                      <div className="flex items-center justify-between rounded-lg border border-gray-200 p-2 transition-colors hover:bg-gray-50">
                        <div className="flex items-center gap-2">
                          {execution.status === "passed" ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          ) : execution.status === "failed" ? (
                            <XCircle className="h-4 w-4 text-red-500" />
                          ) : (
                            <ClockIcon className="h-4 w-4 text-yellow-500" />
                          )}
                          <span className="text-sm">
                            {execution.created_at &&
                              formatDistanceToNow(
                                new Date(execution.created_at),
                                {
                                  addSuffix: true,
                                }
                              )}
                          </span>
                        </div>
                        {execution.execution_time_ms && (
                          <span className="text-xs text-gray-500">
                            {(execution.execution_time_ms / 1000).toFixed(1)}s
                          </span>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
