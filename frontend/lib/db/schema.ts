import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { createId } from "@paralleldrive/cuid2";

// Test Configurations - stores reusable test scenarios
export const testConfigurations = sqliteTable("test_configurations", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  name: text("name").notNull(),
  description: text("description"),
  prompt: text("prompt").notNull(), // User's test prompt (no code required)

  // Network configuration
  networkMode: text("network_mode", { enum: ["low", "high", "default"] })
    .notNull()
    .default("default"),

  // Device configuration
  deviceType: text("device_type", { enum: ["android", "ios", "desktop"] })
    .notNull()
    .default("desktop"),
  deviceVersion: text("device_version"), // e.g., "Android 13", "iOS 17"

  // Screen configuration
  screenWidth: integer("screen_width").default(1920),
  screenHeight: integer("screen_height").default(1080),
  aspectRatio: text("aspect_ratio"), // e.g., "16:9", "4:3"

  // Feature flags (JSON)
  featureFlags: text("feature_flags"), // JSON string of feature flags

  createdAt: integer("created_at", { mode: "timestamp" })
    .$defaultFn(() => new Date()),
  updatedAt: integer("updated_at", { mode: "timestamp" })
    .$defaultFn(() => new Date()),
});

// Configuration Templates - from FastAPI backend system
export const configurationTemplates = sqliteTable("configuration_templates", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  browsers: text("browsers"), // JSON array
  viewports: text("viewports"), // JSON array
  networkModes: text("network_modes"), // JSON array
  userAgentStrings: text("user_agent_strings"), // JSON array
  screenshotOnFailure: integer("screenshot_on_failure", { mode: "boolean" }),
  videoRecording: integer("video_recording", { mode: "boolean" }),
  parallelExecution: integer("parallel_execution", { mode: "boolean" }),
  maxWorkers: integer("max_workers"),
  defaultTimeout: integer("default_timeout"),
  createdAt: text("created_at"),
  updatedAt: text("updated_at"),
});

// Test Executions - stores test runs
export const testExecutions = sqliteTable("test_executions_v2", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  testSuiteId: text("test_suite_id"), // Link to test suite
  configId: text("config_id"),

  // Execution metadata
  status: text("status", { enum: ["pending", "running", "passed", "failed"] })
    .notNull()
    .default("pending"),

  // Execution details
  startedAt: text("started_at"),
  completedAt: text("completed_at"),
  executionTimeMs: integer("execution_time_ms"),
  executionLogs: text("execution_logs"), // JSON
  screenshots: text("screenshots"), // JSON
  videoUrl: text("video_url"),
  errorDetails: text("error_details"),

  // Browser/environment info
  browser: text("browser"),
  viewportWidth: integer("viewport_width"),
  viewportHeight: integer("viewport_height"),
  networkMode: text("network_mode"),

  // Trigger source
  triggeredBy: text("triggered_by"),
  triggeredByUser: text("triggered_by_user"),

  // Slack integration data
  slackChannelId: text("slack_channel_id"),
  slackMessageTs: text("slack_message_ts"),
  slackWorkspace: text("slack_workspace"),

  // GitHub integration data
  githubRepoUrl: text("github_repo_url"),
  githubPrNumber: integer("github_pr_number"),
  githubPrTitle: text("github_pr_title"),
  githubCommitSha: text("github_commit_sha"),

  // Timestamps
  createdAt: text("created_at"),
});

// Integration Settings - stores Slack and GitHub connection info
export const integrationSettings = sqliteTable("integration_settings", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  type: text("type", { enum: ["slack", "github"] }).notNull(),

  // Connection status
  isConnected: integer("is_connected", { mode: "boolean" }).default(false),

  // Slack settings
  slackWorkspaceId: text("slack_workspace_id"),
  slackWorkspaceName: text("slack_workspace_name"),
  slackBotToken: text("slack_bot_token"),
  slackTriggerPatterns: text("slack_trigger_patterns"), // JSON array of patterns

  // GitHub settings
  githubToken: text("github_token"),
  githubMonitoredRepos: text("github_monitored_repos"), // JSON array of repo URLs

  updatedAt: integer("updated_at", { mode: "timestamp" })
    .$defaultFn(() => new Date()),
});

// Test Defaults - stores default test parameters
export const testDefaults = sqliteTable("test_defaults", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),

  // Default configurations
  defaultNetworkMode: text("default_network_mode", {
    enum: ["low", "high", "default"],
  }).default("default"),
  defaultDeviceType: text("default_device_type", {
    enum: ["android", "ios", "desktop"],
  }).default("desktop"),
  defaultScreenWidth: integer("default_screen_width").default(1920),
  defaultScreenHeight: integer("default_screen_height").default(1080),

  updatedAt: integer("updated_at", { mode: "timestamp" })
    .$defaultFn(() => new Date()),
});

// Type exports for TypeScript
export type TestConfiguration = typeof testConfigurations.$inferSelect;
export type NewTestConfiguration = typeof testConfigurations.$inferInsert;

export type TestExecution = typeof testExecutions.$inferSelect;
export type NewTestExecution = typeof testExecutions.$inferInsert;

export type IntegrationSetting = typeof integrationSettings.$inferSelect;
export type NewIntegrationSetting = typeof integrationSettings.$inferInsert;

export type TestDefault = typeof testDefaults.$inferSelect;
export type NewTestDefault = typeof testDefaults.$inferInsert;
