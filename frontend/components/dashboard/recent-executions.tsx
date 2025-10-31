"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TestExecution } from "@/lib/db/schema";
import { formatDistanceToNow } from "date-fns";
import { ArrowRight, CheckCircle2, XCircle, Clock, Loader2 } from "lucide-react";
import Link from "next/link";

interface RecentExecutionsProps {
  executions: TestExecution[];
}

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

export function RecentExecutions({ executions }: RecentExecutionsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Test Executions</CardTitle>
      </CardHeader>
      <CardContent>
        {executions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Clock className="mb-2 h-8 w-8 text-gray-400" />
            <p className="text-sm text-gray-500">No test executions yet</p>
            <p className="mt-1 text-xs text-gray-400">
              Create a test configuration and run your first test
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {executions.map((execution) => {
              const config = statusConfig[execution.status];
              const StatusIcon = config.icon;

              return (
                <div
                  key={execution.id}
                  className="flex items-center justify-between rounded-lg border p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-4">
                    <StatusIcon
                      className={`h-5 w-5 ${
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
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Test Execution</span>
                        <Badge variant={config.color as any}>
                          {config.label}
                        </Badge>
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                        <span>Triggered by: {execution.triggeredBy}</span>
                        {execution.createdAt && (
                          <>
                            <span>•</span>
                            <span>
                              {formatDistanceToNow(new Date(execution.createdAt), {
                                addSuffix: true,
                              })}
                            </span>
                          </>
                        )}
                        {execution.githubPrNumber && (
                          <>
                            <span>•</span>
                            <span>PR #{execution.githubPrNumber}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <Link href={`/test-executions/${execution.id}`}>
                    <Button variant="ghost" size="sm">
                      View
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
