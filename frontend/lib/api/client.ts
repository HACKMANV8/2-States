/**
 * TestGPT Backend API Client
 *
 * TypeScript client for communicating with the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface TestStep {
  step_number: number;
  action: string;
  target: string;
  expected_outcome: string;
  timeout_seconds?: number;
  value?: string;
}

export interface TestSuite {
  id: string;
  name: string;
  description?: string;
  prompt: string;
  target_url: string;
  test_steps: TestStep[];
  created_at: string;
  last_run?: string;
  created_by?: string;
  source_type: string;
  tags: string[];
}

export interface TestSuiteListItem {
  id: string;
  name: string;
  description?: string;
  target_url: string;
  created_at: string;
  last_run?: string;
  tags: string[];
}

export interface ViewportConfig {
  width: number;
  height: number;
  device_name: string;
}

export interface ConfigurationTemplate {
  id: string;
  name: string;
  description?: string;
  browsers: string[];
  viewports: ViewportConfig[];
  network_modes: string[];
  user_agent_strings?: string[];
  screenshot_on_failure: boolean;
  video_recording: boolean;
  parallel_execution: boolean;
  max_workers: number;
  default_timeout: number;
  created_at: string;
  updated_at: string;
}

export interface TestExecution {
  id: string;
  test_suite_id?: string;
  config_id?: string;
  status: "pending" | "running" | "passed" | "failed";
  started_at?: string;
  completed_at?: string;
  execution_time_ms?: number;
  execution_logs?: any[];
  screenshots?: string[];
  video_url?: string;
  error_details?: string;
  browser?: string;
  viewport_width?: number;
  viewport_height?: number;
  network_mode?: string;
  triggered_by: string;
  triggered_by_user?: string;
  created_at: string;
}

export interface ExecutionHistory {
  test_suite_id: string;
  test_suite_name: string;
  executions: TestExecution[];
  total_runs: number;
  passed_runs: number;
  failed_runs: number;
}

export interface TestStatistics {
  total_test_suites: number;
  total_executions: number;
  passed_executions: number;
  failed_executions: number;
  running_executions: number;
  average_execution_time_ms?: number;
  most_run_test?: any;
  recent_failures: TestExecution[];
}

// ============================================================================
// API CLIENT CLASS
// ============================================================================

class TestGPTApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || "API request failed");
    }

    return response.json();
  }

  // ==========================================================================
  // TEST SUITE ENDPOINTS
  // ==========================================================================

  async createTestSuite(data: {
    name: string;
    description?: string;
    prompt: string;
    target_url: string;
    test_steps: TestStep[];
    created_by?: string;
    source_type?: "slack_trigger" | "github_pr" | "manual";
    tags?: string[];
  }): Promise<TestSuite> {
    return this.request<TestSuite>("/api/tests", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listTestSuites(params?: {
    skip?: number;
    limit?: number;
    tags?: string;
    search?: string;
  }): Promise<TestSuiteListItem[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append("skip", params.skip.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.tags) queryParams.append("tags", params.tags);
    if (params?.search) queryParams.append("search", params.search);

    return this.request<TestSuiteListItem[]>(
      `/api/tests?${queryParams.toString()}`
    );
  }

  async getTestSuite(testId: string): Promise<TestSuite> {
    return this.request<TestSuite>(`/api/tests/${testId}`);
  }

  async updateTestSuite(
    testId: string,
    data: {
      name?: string;
      description?: string;
      test_steps?: TestStep[];
      tags?: string[];
    }
  ): Promise<TestSuite> {
    return this.request<TestSuite>(`/api/tests/${testId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTestSuite(testId: string): Promise<{ status: string; id: string }> {
    return this.request(`/api/tests/${testId}`, {
      method: "DELETE",
    });
  }

  // ==========================================================================
  // CONFIGURATION TEMPLATE ENDPOINTS
  // ==========================================================================

  async createConfig(data: {
    name: string;
    description?: string;
    browsers?: string[];
    viewports?: ViewportConfig[];
    network_modes?: string[];
    screenshot_on_failure?: boolean;
    video_recording?: boolean;
    parallel_execution?: boolean;
    max_workers?: number;
    default_timeout?: number;
  }): Promise<ConfigurationTemplate> {
    return this.request<ConfigurationTemplate>("/api/configs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listConfigs(params?: {
    skip?: number;
    limit?: number;
  }): Promise<ConfigurationTemplate[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append("skip", params.skip.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());

    return this.request<ConfigurationTemplate[]>(
      `/api/configs?${queryParams.toString()}`
    );
  }

  async getConfig(configId: string): Promise<ConfigurationTemplate> {
    return this.request<ConfigurationTemplate>(`/api/configs/${configId}`);
  }

  async updateConfig(
    configId: string,
    data: Partial<ConfigurationTemplate>
  ): Promise<ConfigurationTemplate> {
    return this.request<ConfigurationTemplate>(`/api/configs/${configId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteConfig(configId: string): Promise<{ status: string; id: string }> {
    return this.request(`/api/configs/${configId}`, {
      method: "DELETE",
    });
  }

  // ==========================================================================
  // TEST EXECUTION ENDPOINTS
  // ==========================================================================

  async runTest(
    testId: string,
    data: {
      config_id?: string;
      browser?: string;
      viewport_width?: number;
      viewport_height?: number;
      network_mode?: string;
      triggered_by?: "slack" | "manual" | "github";
      triggered_by_user?: string;
    }
  ): Promise<TestExecution> {
    return this.request<TestExecution>(`/api/tests/${testId}/run`, {
      method: "POST",
      body: JSON.stringify({
        test_suite_id: testId,
        ...data,
      }),
    });
  }

  async listExecutions(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    test_suite_id?: string;
  }): Promise<TestExecution[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append("skip", params.skip.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.status) queryParams.append("status", params.status);
    if (params?.test_suite_id)
      queryParams.append("test_suite_id", params.test_suite_id);

    return this.request<TestExecution[]>(
      `/api/executions?${queryParams.toString()}`
    );
  }

  async getExecution(executionId: string): Promise<TestExecution> {
    return this.request<TestExecution>(`/api/executions/${executionId}`);
  }

  async getTestHistory(
    testId: string,
    limit: number = 50
  ): Promise<ExecutionHistory> {
    return this.request<ExecutionHistory>(
      `/api/tests/${testId}/history?limit=${limit}`
    );
  }

  // ==========================================================================
  // BATCH EXECUTION
  // ==========================================================================

  async runBatchTests(data: {
    test_suite_ids: string[];
    config_id: string;
    triggered_by?: "slack" | "manual" | "github";
    triggered_by_user?: string;
  }): Promise<{
    batch_id: string;
    execution_ids: string[];
    total_tests: number;
    status: string;
  }> {
    return this.request("/api/tests/batch/run", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ==========================================================================
  // STATISTICS
  // ==========================================================================

  async getStatistics(): Promise<TestStatistics> {
    return this.request<TestStatistics>("/api/statistics");
  }

  // ==========================================================================
  // MIGRATION
  // ==========================================================================

  async migrateJsonToDb(): Promise<{
    status: string;
    migrated: number;
    errors: any[];
  }> {
    return this.request("/api/migrate/json-to-db", {
      method: "POST",
    });
  }
}

// Export singleton instance
export const apiClient = new TestGPTApiClient();

// Export class for custom instances
export default TestGPTApiClient;
