CREATE TABLE `integration_settings` (
	`id` text PRIMARY KEY NOT NULL,
	`type` text NOT NULL,
	`is_connected` integer DEFAULT false,
	`slack_workspace_id` text,
	`slack_workspace_name` text,
	`slack_bot_token` text,
	`slack_trigger_patterns` text,
	`github_token` text,
	`github_monitored_repos` text,
	`updated_at` integer
);
--> statement-breakpoint
CREATE TABLE `test_configurations` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`description` text,
	`prompt` text NOT NULL,
	`network_mode` text DEFAULT 'default' NOT NULL,
	`device_type` text DEFAULT 'desktop' NOT NULL,
	`device_version` text,
	`screen_width` integer DEFAULT 1920,
	`screen_height` integer DEFAULT 1080,
	`aspect_ratio` text,
	`feature_flags` text,
	`created_at` integer,
	`updated_at` integer
);
--> statement-breakpoint
CREATE TABLE `test_defaults` (
	`id` text PRIMARY KEY NOT NULL,
	`default_network_mode` text DEFAULT 'default',
	`default_device_type` text DEFAULT 'desktop',
	`default_screen_width` integer DEFAULT 1920,
	`default_screen_height` integer DEFAULT 1080,
	`updated_at` integer
);
--> statement-breakpoint
CREATE TABLE `test_executions` (
	`id` text PRIMARY KEY NOT NULL,
	`config_id` text,
	`status` text DEFAULT 'pending' NOT NULL,
	`triggered_by` text DEFAULT 'manual' NOT NULL,
	`triggered_by_user` text,
	`slack_channel_id` text,
	`slack_message_ts` text,
	`slack_workspace` text,
	`github_repo_url` text,
	`github_pr_number` integer,
	`github_pr_title` text,
	`github_commit_sha` text,
	`playwright_output` text,
	`ai_generated_tests` text,
	`screenshot_urls` text,
	`execution_time_ms` integer,
	`network_simulation_results` text,
	`error_message` text,
	`error_stack` text,
	`started_at` integer,
	`completed_at` integer,
	`created_at` integer,
	FOREIGN KEY (`config_id`) REFERENCES `test_configurations`(`id`) ON UPDATE no action ON DELETE set null
);
