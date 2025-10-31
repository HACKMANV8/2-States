"use client";

import { useState, useEffect } from 'react';
import { PRTestResults } from '@/components/PRTestResults';

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
  slack_message_posted: boolean;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}

export default function PRTestsPage() {
  const [tests, setTests] = useState<PRTestResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPRTests();
  }, []);

  const fetchPRTests = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/pr-tests/?limit=50');

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTests(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch PR tests:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch PR tests');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">PR Test Runs</h1>
        <p className="text-gray-600">
          View and manage pull request test executions triggered from Slack
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <span className="text-red-600 font-semibold">Error:</span>
            <span className="text-red-800">{error}</span>
          </div>
          <button
            onClick={fetchPRTests}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      <PRTestResults tests={tests} loading={loading} />

      {!loading && !error && tests.length > 0 && (
        <div className="mt-6 text-center">
          <button
            onClick={fetchPRTests}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Refresh
          </button>
        </div>
      )}
    </div>
  );
}
