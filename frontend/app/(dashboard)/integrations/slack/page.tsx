import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  MessageSquare,
  CheckCircle2,
  XCircle,
  ExternalLink,
  RefreshCw,
} from "lucide-react";

export const dynamic = "force-dynamic";

export default function SlackIntegrationPage() {
  // Placeholder data - will be replaced with actual API calls
  const isConnected = false;
  const workspaceName = "";
  const triggerPatterns = ["@TestGPT", "@test-gpt"];

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Slack Integration
        </h1>
        <p className="mt-2 text-gray-500">
          Connect TestGPT to your Slack workspace to trigger tests via messages
        </p>
      </div>

      <div className="space-y-6">
        {/* Connection Status */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <MessageSquare className="h-8 w-8 text-gray-600" />
                <div>
                  <CardTitle>Connection Status</CardTitle>
                  <CardDescription>
                    {isConnected
                      ? `Connected to ${workspaceName}`
                      : "Not connected to Slack"}
                  </CardDescription>
                </div>
              </div>
              {isConnected ? (
                <Badge variant="success" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  Connected
                </Badge>
              ) : (
                <Badge variant="secondary" className="gap-1">
                  <XCircle className="h-3 w-3" />
                  Disconnected
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {!isConnected ? (
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Connect TestGPT to your Slack workspace to enable automated
                  testing triggered by Slack messages. Once connected, you can
                  mention TestGPT in any channel with test instructions.
                </p>
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <h4 className="mb-2 text-sm font-medium">How it works:</h4>
                  <ol className="list-inside list-decimal space-y-1 text-sm text-gray-600">
                    <li>Click "Connect to Slack" to authorize the integration</li>
                    <li>Select the workspace you want to connect</li>
                    <li>TestGPT will be added as a bot to your workspace</li>
                    <li>
                      Mention @TestGPT in any channel with your test instructions
                    </li>
                    <li>TestGPT will execute the tests and post results back</li>
                  </ol>
                </div>
                <Button className="w-full" size="lg">
                  <MessageSquare className="mr-2 h-5 w-5" />
                  Connect to Slack
                  <ExternalLink className="ml-2 h-4 w-4" />
                </Button>
                <p className="text-center text-xs text-gray-500">
                  You'll be redirected to Slack to authorize the connection
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <div>
                      <h4 className="font-medium text-green-900">
                        Successfully connected to {workspaceName}
                      </h4>
                      <p className="mt-1 text-sm text-green-700">
                        TestGPT is now listening for trigger messages in your
                        Slack workspace.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Button variant="outline" className="flex-1">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Reconnect
                  </Button>
                  <Button variant="destructive" className="flex-1">
                    Disconnect
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trigger Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Trigger Configuration</CardTitle>
            <CardDescription>
              Configure how TestGPT responds to Slack messages
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="trigger-patterns">
                Trigger Patterns (one per line)
              </Label>
              <Textarea
                id="trigger-patterns"
                placeholder="@TestGPT&#10;@test-gpt&#10;/test"
                defaultValue={triggerPatterns.join("\n")}
                className="min-h-[100px] font-mono text-sm"
                disabled={!isConnected}
              />
              <p className="mt-2 text-xs text-gray-500">
                TestGPT will respond to messages containing these patterns.
                Patterns are case-insensitive.
              </p>
            </div>

            <div className="rounded-lg border bg-gray-50 p-4">
              <h4 className="mb-2 text-sm font-medium">Example Usage:</h4>
              <div className="space-y-2 text-sm">
                <div className="font-mono rounded bg-white p-2 border">
                  @TestGPT Please test the login flow on Android with low bandwidth
                </div>
                <div className="font-mono rounded bg-white p-2 border">
                  @test-gpt Run tests for PR #123
                </div>
              </div>
            </div>

            <Button disabled={!isConnected}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Save Configuration
            </Button>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Notification Settings</CardTitle>
            <CardDescription>
              Configure how test results are posted to Slack
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Post results in thread
                  </div>
                  <div className="text-xs text-gray-500">
                    Reply to the trigger message with test results
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  disabled={!isConnected}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Notify on test completion
                  </div>
                  <div className="text-xs text-gray-500">
                    Send notification when tests finish
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  disabled={!isConnected}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Include screenshots
                  </div>
                  <div className="text-xs text-gray-500">
                    Attach test screenshots to Slack messages
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  disabled={!isConnected}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>

            <Button disabled={!isConnected}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Save Notification Settings
            </Button>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Slack Activity</CardTitle>
            <CardDescription>
              Test executions triggered from Slack
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <MessageSquare className="mb-2 h-8 w-8 text-gray-400" />
              <p className="text-sm text-gray-500">
                {isConnected
                  ? "No Slack-triggered tests yet"
                  : "Connect to Slack to see activity"}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
