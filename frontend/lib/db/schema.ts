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

// Test Executions - stores test runs
export const testExecutions = sqliteTable("test_executions", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  configId: text("config_id").references(() => testConfigurations.id, {
    onDelete: "set null",
  }),

  // Execution metadata
  status: text("status", { enum: ["pending", "running", "passed", "failed"] })
    .notNull()
    .default("pending"),

  // Trigger source
  triggeredBy: text("triggered_by", { enum: ["slack", "manual", "github"] })
    .notNull()
    .default("manual"),
  triggeredByUser: text("triggered_by_user"), // Username or Slack user ID

  // Slack integration data
  slackChannelId: text("slack_channel_id"),
  slackMessageTs: text("slack_message_ts"),
  slackWorkspace: text("slack_workspace"),

  // GitHub integration data
  githubRepoUrl: text("github_repo_url"),
  githubPrNumber: integer("github_pr_number"),
  githubPrTitle: text("github_pr_title"),
  githubCommitSha: text("github_commit_sha"),

  // Test results
  playwrightOutput: text("playwright_output"), // Full Playwright logs
  aiGeneratedTests: text("ai_generated_tests"), // AI-generated test code (for re-running)
  screenshotUrls: text("screenshot_urls"), // JSON array of screenshot URLs

  // Performance metrics
  executionTimeMs: integer("execution_time_ms"),
  networkSimulationResults: text("network_simulation_results"), // JSON

  // Error information
  errorMessage: text("error_message"),
  errorStack: text("error_stack"),

  startedAt: integer("started_at", { mode: "timestamp" }),
  completedAt: integer("completed_at", { mode: "timestamp" }),
  createdAt: integer("created_at", { mode: "timestamp" })
    .$defaultFn(() => new Date()),
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
