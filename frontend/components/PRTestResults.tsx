/**
 * PR Test Results Component
 *
 * Displays PR test run results in the TestGPT frontend.
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

interface PRTestResult {
  id: string;
  pr_url: string;
  pr_number: number;
  pr_title: string;
  pr_author: string | null;
  repo_owner: string;
  repo_name: string;
  deployment_url: string | null;
  deployment_platform: string | null;
  project_type: string | null;
  framework_detected: string | null;
  status: string;
  overall_pass: boolean | null;
  scenarios_passed: number;
  scenarios_failed: number;
  scenarios_total: number;
  duration_ms: number | null;
  github_comment_posted: boolean;
  github_comment_url: string | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}

interface PRTestResultsProps {
  tests: PRTestResult[];
  loading?: boolean;
}

export function PRTestResults({ tests, loading = false }: PRTestResultsProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading PR tests...</div>
      </div>
    );
  }

  if (tests.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">No PR tests found</p>
          <p className="text-sm text-gray-400 mt-2">
            PR tests will appear here after running tests via Slack
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {tests.map((test) => (
        <PRTestCard key={test.id} test={test} />
      ))}
    </div>
  );
}

function PRTestCard({ test }: { test: PRTestResult }) {
  const getStatusBadge = (status: string) => {
    const variants: Record<string, "success" | "destructive" | "secondary" | "outline"> = {
      passed: "success",
      failed: "destructive",
      running: "secondary",
      error: "destructive",
      pending: "outline",
    };

    return (
      <Badge variant={variants[status] || "outline"}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  const formatDuration = (ms: number | null) => {
    if (!ms) return "N/A";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">
              <a
                href={test.pr_url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline text-blue-600"
              >
                {test.pr_title}
              </a>
            </CardTitle>
            <CardDescription>
              {test.repo_owner}/{test.repo_name} #{test.pr_number}
              {test.pr_author && ` by @${test.pr_author}`}
            </CardDescription>
          </div>
          <div className="flex flex-col items-end gap-2">
            {getStatusBadge(test.status)}
            {test.framework_detected && (
              <Badge variant="outline">{test.framework_detected}</Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <div className="text-sm text-gray-500">Test Results</div>
            <div className="text-lg font-semibold">
              {test.scenarios_passed}/{test.scenarios_total}
            </div>
            <div className="text-xs text-gray-500">scenarios passed</div>
          </div>

          <div>
            <div className="text-sm text-gray-500">Duration</div>
            <div className="text-lg font-semibold">
              {formatDuration(test.duration_ms)}
            </div>
            <div className="text-xs text-gray-500">execution time</div>
          </div>

          <div>
            <div className="text-sm text-gray-500">Project Type</div>
            <div className="text-lg font-semibold capitalize">
              {test.project_type || "N/A"}
            </div>
            <div className="text-xs text-gray-500">detected</div>
          </div>

          <div>
            <div className="text-sm text-gray-500">Deployment</div>
            <div className="text-lg font-semibold">
              {test.deployment_platform || "N/A"}
            </div>
            {test.deployment_url && (
              <a
                href={test.deployment_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-600 hover:underline"
              >
                View deployment
              </a>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500 pt-4 border-t">
          <span>
            Started: {new Date(test.started_at).toLocaleString()}
          </span>
          {test.github_comment_posted && test.github_comment_url && (
            <a
              href={test.github_comment_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              View GitHub comment →
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default PRTestResults;
