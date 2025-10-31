"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { apiClient, TestSuite, ConfigurationTemplate } from "@/lib/api/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PlayCircle, ArrowLeft, Loader2, Settings, MessageSquare } from "lucide-react";
import Link from "next/link";

export default function RunTestPage({
  params,
}: {
  params: Promise<{ testId: string }>;
}) {
  const router = useRouter();
  const { testId } = use(params);
  const [testSuite, setTestSuite] = useState<TestSuite | null>(null);
  const [configs, setConfigs] = useState<ConfigurationTemplate[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<string>("custom");
  const [selectedBrowser, setSelectedBrowser] = useState<string>("chrome");
  const [selectedViewport, setSelectedViewport] = useState<string>("desktop");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (testId) {
      loadData();
    }
  }, [testId]);

  const loadData = async () => {
    if (!testId) return;

    try {
      const [suite, configList] = await Promise.all([
        apiClient.getTestSuite(testId),
        apiClient.listConfigs({ limit: 100 }),
      ]);

      setTestSuite(suite);
      setConfigs(configList);

      // Set default config if available
      if (configList.length > 0) {
        setSelectedConfig(configList[0].id);
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async () => {
    if (!testSuite) return;

    setRunning(true);

    try {
      // Determine viewport dimensions
      const viewportDimensions: { [key: string]: { width: number; height: number } } = {
        "mobile": { width: 375, height: 667 },
        "tablet": { width: 768, height: 1024 },
        "desktop": { width: 1920, height: 1080 },
      };

      const viewport = viewportDimensions[selectedViewport] || viewportDimensions.desktop;

      const execution = await apiClient.runTest(testId, {
        config_id: selectedConfig === "custom" ? undefined : selectedConfig,
        browser: selectedBrowser,
        viewport_width: viewport.width,
        viewport_height: viewport.height,
        triggered_by: "manual",
      });

      // Redirect to execution page
      router.push(`/test-executions/${execution.id}`);
    } catch (error) {
      console.error("Failed to run test:", error);
      alert("Failed to start test execution. Please try again.");
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!testSuite) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold">Test suite not found</h2>
          <Link href="/test-library">
            <Button className="mt-4" variant="outline">
              Back to Library
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const selectedConfigData = selectedConfig !== "custom" ? configs.find((c) => c.id === selectedConfig) : null;

  // Build dynamic Slack command based on selections
  const buildSlackCommand = () => {
    let command = `@TestGPT test ${testSuite?.target_url}`;

    // Add browser if not default
    if (selectedBrowser !== "chrome") {
      command += ` browser:${selectedBrowser}`;
    }

    // Add viewport if not default
    if (selectedViewport !== "desktop") {
      command += ` viewport:${selectedViewport}`;
    }

    return command;
  };

  return (
    <div className="mx-auto max-w-4xl p-6">
      {/* Header */}
      <div className="mb-6">
        <Link href={`/test-library/${testId}`}>
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Test Details
          </Button>
        </Link>

        <h1 className="text-3xl font-bold text-gray-900">Run Test</h1>
        <p className="mt-2 text-gray-600">{testSuite.name}</p>
      </div>

      {/* Run Button - Two Options */}
      <Card className="mb-6 border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <PlayCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 mb-2">Two Ways to Run Tests</h3>
                <div className="space-y-2 text-sm text-green-800">
                  <div>
                    <strong>1. API (Direct):</strong> Click the button below to execute immediately via API
                  </div>
                  <div>
                    <strong>2. Slack (Recommended):</strong> Copy the command above for interactive execution in Slack
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Link href={`/test-library/${testId}`}>
                <Button variant="outline" disabled={running}>
                  Cancel
                </Button>
              </Link>
              <Button onClick={handleRun} disabled={running} size="lg">
                {running ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Starting Test...
                  </>
                ) : (
                  <>
                    <PlayCircle className="mr-2 h-5 w-5" />
                    Run Test via API
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Slack Instructions */}
      <Card className="mb-6 border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <MessageSquare className="h-6 w-6 text-blue-600 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900 mb-2">Execute in Slack</h3>
                <p className="text-sm text-blue-800 mb-3">
                  Copy this command and paste it in Slack to run the test:
                </p>
                <div className="rounded bg-white p-3 font-mono text-sm border border-blue-200 break-all select-all">
                  {buildSlackCommand()}
                </div>
                <p className="text-xs text-blue-700 mt-2">
                  💡 The AI agent will execute your test steps automatically with Playwright
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-6">
        {/* Configuration Template */}
        <Card>
          <CardHeader>
            <CardTitle>Configuration Template</CardTitle>
            <CardDescription>
              Select a predefined configuration or customize individual settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="config">Configuration Preset</Label>
                <Select value={selectedConfig} onValueChange={setSelectedConfig}>
                  <SelectTrigger id="config">
                    <SelectValue placeholder="Select a configuration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="custom">Custom Configuration</SelectItem>
                    {configs.map((config) => (
                      <SelectItem key={config.id} value={config.id}>
                        {config.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedConfigData && (
                  <p className="mt-2 text-sm text-gray-500">
                    {selectedConfigData.description}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Browser Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Browser</CardTitle>
            <CardDescription>Select the browser engine to use</CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedBrowser} onValueChange={setSelectedBrowser}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="chrome">Chrome</SelectItem>
                <SelectItem value="firefox">Firefox</SelectItem>
                <SelectItem value="safari">Safari (WebKit)</SelectItem>
                <SelectItem value="edge">Edge</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Viewport Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Viewport</CardTitle>
            <CardDescription>Select the screen size to test</CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedViewport} onValueChange={setSelectedViewport}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="mobile">Mobile (375x667)</SelectItem>
                <SelectItem value="tablet">Tablet (768x1024)</SelectItem>
                <SelectItem value="desktop">Desktop (1920x1080)</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
