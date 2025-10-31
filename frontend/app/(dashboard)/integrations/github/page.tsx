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
import {
  Github,
  CheckCircle2,
  XCircle,
  ExternalLink,
  RefreshCw,
  Plus,
  Trash2,
  GitPullRequest,
} from "lucide-react";

export const dynamic = "force-dynamic";

export default function GitHubIntegrationPage() {
  // Placeholder data - will be replaced with actual API calls
  const isConnected = false;
  const monitoredRepos: Array<{ url: string; active: boolean }> = [
    // Placeholder examples
    // { url: "https://github.com/example/repo1", active: true },
    // { url: "https://github.com/example/repo2", active: true },
  ];

  const recentPRs: Array<{ number: number; title: string; repo: string; status: string }> = [
    // Placeholder examples
    // { number: 123, title: "Add new feature", repo: "example/repo1", status: "passed" },
  ];

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          GitHub Integration
        </h1>
        <p className="mt-2 text-gray-500">
          Connect TestGPT to GitHub to automatically test pull requests
        </p>
      </div>

      <div className="space-y-6">
        {/* Connection Status */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Github className="h-8 w-8 text-gray-600" />
                <div>
                  <CardTitle>Connection Status</CardTitle>
                  <CardDescription>
                    {isConnected
                      ? "Connected to GitHub"
                      : "Not connected to GitHub"}
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
                  Connect TestGPT to GitHub to automatically trigger tests when
                  pull requests are opened or updated. TestGPT will post test
                  results as PR comments and update check statuses.
                </p>
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <h4 className="mb-2 text-sm font-medium">How it works:</h4>
                  <ol className="list-inside list-decimal space-y-1 text-sm text-gray-600">
                    <li>Click "Connect to GitHub" to authorize the integration</li>
                    <li>Grant TestGPT access to your repositories</li>
                    <li>Configure which repositories to monitor</li>
                    <li>TestGPT will listen for PR events</li>
                    <li>Tests run automatically and results are posted to PRs</li>
                  </ol>
                </div>
                <Button className="w-full" size="lg">
                  <Github className="mr-2 h-5 w-5" />
                  Connect to GitHub
                  <ExternalLink className="ml-2 h-4 w-4" />
                </Button>
                <p className="text-center text-xs text-gray-500">
                  You'll be redirected to GitHub to authorize the connection
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <div>
                      <h4 className="font-medium text-green-900">
                        Successfully connected to GitHub
                      </h4>
                      <p className="mt-1 text-sm text-green-700">
                        TestGPT is now monitoring your configured repositories
                        for pull request events.
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

        {/* Monitored Repositories */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Monitored Repositories</CardTitle>
                <CardDescription>
                  Repositories that TestGPT is watching for PRs
                </CardDescription>
              </div>
              <Button size="sm" disabled={!isConnected}>
                <Plus className="mr-2 h-4 w-4" />
                Add Repository
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {monitoredRepos.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Github className="mb-2 h-8 w-8 text-gray-400" />
                <p className="text-sm text-gray-500">
                  {isConnected
                    ? "No repositories configured yet"
                    : "Connect to GitHub to add repositories"}
                </p>
                {isConnected && (
                  <Button variant="outline" size="sm" className="mt-4">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Your First Repository
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {monitoredRepos.map((repo, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div className="flex items-center gap-3">
                      <Github className="h-5 w-5 text-gray-500" />
                      <div>
                        <div className="font-medium">{repo.url}</div>
                        <div className="text-xs text-gray-500">
                          {repo.active ? "Active monitoring" : "Paused"}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm">
                        Configure
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {isConnected && (
              <div className="mt-4 space-y-3">
                <Label htmlFor="repo-url">Add Repository URL</Label>
                <div className="flex gap-2">
                  <Input
                    id="repo-url"
                    placeholder="https://github.com/username/repo"
                    className="flex-1"
                  />
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Add
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* PR Trigger Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Pull Request Triggers</CardTitle>
            <CardDescription>
              Configure when tests should be triggered
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Test on PR opened
                  </div>
                  <div className="text-xs text-gray-500">
                    Run tests when a new PR is created
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
                    Test on PR updated
                  </div>
                  <div className="text-xs text-gray-500">
                    Run tests when commits are pushed to a PR
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
                    Test on PR comment
                  </div>
                  <div className="text-xs text-gray-500">
                    Re-run tests when specific comment is posted
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

            <div className="rounded-lg border bg-gray-50 p-4">
              <Label htmlFor="trigger-comment" className="mb-2 block">
                Re-test Trigger Comment
              </Label>
              <Input
                id="trigger-comment"
                defaultValue="/test"
                disabled={!isConnected}
                className="mb-2"
              />
              <p className="text-xs text-gray-500">
                Post this comment on a PR to manually trigger tests
              </p>
            </div>

            <Button disabled={!isConnected}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Save Configuration
            </Button>
          </CardContent>
        </Card>

        {/* Recent PR Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Pull Request Activity</CardTitle>
            <CardDescription>
              PRs that triggered test executions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recentPRs.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <GitPullRequest className="mb-2 h-8 w-8 text-gray-400" />
                <p className="text-sm text-gray-500">
                  {isConnected
                    ? "No PR-triggered tests yet"
                    : "Connect to GitHub to see activity"}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentPRs.map((pr) => (
                  <div
                    key={pr.number}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div className="flex items-center gap-3">
                      <GitPullRequest className="h-5 w-5 text-gray-500" />
                      <div>
                        <div className="font-medium">
                          #{pr.number}: {pr.title}
                        </div>
                        <div className="text-xs text-gray-500">{pr.repo}</div>
                      </div>
                    </div>
                    <Badge
                      variant={
                        pr.status === "passed" ? "success" : "destructive"
                      }
                    >
                      {pr.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Check Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>GitHub Check Configuration</CardTitle>
            <CardDescription>
              How test results appear on pull requests
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Post check status
                  </div>
                  <div className="text-xs text-gray-500">
                    Update PR check status with test results
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
                    Comment on PR
                  </div>
                  <div className="text-xs text-gray-500">
                    Post detailed test results as a PR comment
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
                    Block merge on failure
                  </div>
                  <div className="text-xs text-gray-500">
                    Require passing tests before PR can be merged
                  </div>
                </div>
                <input
                  type="checkbox"
                  disabled={!isConnected}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>

            <Button disabled={!isConnected}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Save Check Configuration
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
