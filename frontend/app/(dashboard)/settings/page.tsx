import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Settings as SettingsIcon, Save } from "lucide-react";

export const dynamic = "force-dynamic";

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-500">
          Configure default test parameters and application settings
        </p>
      </div>

      <div className="space-y-6">
        {/* Default Test Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Default Test Configuration</CardTitle>
            <CardDescription>
              Set default values for new test configurations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="default-network">Default Network Mode</Label>
              <Select defaultValue="default">
                <SelectTrigger id="default-network">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default (No Throttling)</SelectItem>
                  <SelectItem value="low">Low Bandwidth (3G)</SelectItem>
                  <SelectItem value="high">High Bandwidth (4G/5G)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="default-device">Default Device Type</Label>
              <Select defaultValue="desktop">
                <SelectTrigger id="default-device">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="desktop">Desktop</SelectItem>
                  <SelectItem value="android">Android</SelectItem>
                  <SelectItem value="ios">iOS</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="default-width">Default Screen Width</Label>
                <Input
                  id="default-width"
                  type="number"
                  defaultValue={1920}
                  placeholder="1920"
                />
              </div>
              <div>
                <Label htmlFor="default-height">Default Screen Height</Label>
                <Input
                  id="default-height"
                  type="number"
                  defaultValue={1080}
                  placeholder="1080"
                />
              </div>
            </div>

            <Button>
              <Save className="mr-2 h-4 w-4" />
              Save Default Configuration
            </Button>
          </CardContent>
        </Card>

        {/* Test Execution Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Test Execution Settings</CardTitle>
            <CardDescription>
              Configure how tests are executed
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="max-concurrent">
                Maximum Concurrent Tests
              </Label>
              <Input
                id="max-concurrent"
                type="number"
                defaultValue={3}
                placeholder="3"
                min={1}
                max={10}
              />
              <p className="mt-2 text-xs text-gray-500">
                Number of tests that can run simultaneously
              </p>
            </div>

            <div>
              <Label htmlFor="test-timeout">
                Test Timeout (seconds)
              </Label>
              <Input
                id="test-timeout"
                type="number"
                defaultValue={300}
                placeholder="300"
                min={30}
                max={3600}
              />
              <p className="mt-2 text-xs text-gray-500">
                Maximum time allowed for a single test execution
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Auto-retry failed tests
                  </div>
                  <div className="text-xs text-gray-500">
                    Automatically retry tests that fail once
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Capture screenshots on failure
                  </div>
                  <div className="text-xs text-gray-500">
                    Automatically take screenshots when tests fail
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Save test artifacts
                  </div>
                  <div className="text-xs text-gray-500">
                    Store videos and traces for debugging
                  </div>
                </div>
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>

            <Button>
              <Save className="mr-2 h-4 w-4" />
              Save Execution Settings
            </Button>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Notification Settings</CardTitle>
            <CardDescription>
              Configure how you receive test notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Email notifications
                  </div>
                  <div className="text-xs text-gray-500">
                    Receive email alerts for test results
                  </div>
                </div>
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Only notify on failures
                  </div>
                  <div className="text-xs text-gray-500">
                    Only send notifications when tests fail
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="notification-email">
                Notification Email
              </Label>
              <Input
                id="notification-email"
                type="email"
                placeholder="you@example.com"
              />
            </div>

            <Button>
              <Save className="mr-2 h-4 w-4" />
              Save Notification Settings
            </Button>
          </CardContent>
        </Card>

        {/* Advanced Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Advanced Settings</CardTitle>
            <CardDescription>
              Advanced configuration options
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="playwright-version">
                Playwright Version
              </Label>
              <Select defaultValue="latest">
                <SelectTrigger id="playwright-version">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="latest">Latest (Recommended)</SelectItem>
                  <SelectItem value="1.40">1.40</SelectItem>
                  <SelectItem value="1.39">1.39</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Enable headless mode
                  </div>
                  <div className="text-xs text-gray-500">
                    Run tests in headless browser mode
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">
                    Enable debug logging
                  </div>
                  <div className="text-xs text-gray-500">
                    Show detailed debug logs for troubleshooting
                  </div>
                </div>
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>

            <Button>
              <Save className="mr-2 h-4 w-4" />
              Save Advanced Settings
            </Button>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card>
          <CardHeader>
            <CardTitle>Data Management</CardTitle>
            <CardDescription>
              Manage your test data and storage
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
              <div className="text-sm">
                <span className="font-medium text-yellow-900">
                  Storage Usage:
                </span>{" "}
                <span className="text-yellow-700">
                  234 MB of 1 GB used
                </span>
              </div>
            </div>

            <div className="space-y-3">
              <Button variant="outline" className="w-full">
                Export Test Data
              </Button>
              <Button variant="outline" className="w-full">
                Clear Test History
              </Button>
              <Button variant="destructive" className="w-full">
                Delete All Data
              </Button>
            </div>

            <p className="text-xs text-gray-500">
              Deleting data is permanent and cannot be undone
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
