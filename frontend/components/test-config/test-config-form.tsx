"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TestConfiguration } from "@/lib/db/schema";
import { Loader2, Save } from "lucide-react";

interface TestConfigFormProps {
  initialData?: Partial<TestConfiguration>;
  onSubmit: (data: Partial<TestConfiguration>) => Promise<void>;
}

export function TestConfigForm({ initialData, onSubmit }: TestConfigFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<TestConfiguration>>({
    name: initialData?.name || "",
    description: initialData?.description || "",
    prompt: initialData?.prompt || "",
    networkMode: initialData?.networkMode || "default",
    deviceType: initialData?.deviceType || "desktop",
    deviceVersion: initialData?.deviceVersion || "",
    screenWidth: initialData?.screenWidth || 1920,
    screenHeight: initialData?.screenHeight || 1080,
    aspectRatio: initialData?.aspectRatio || "16:9",
    featureFlags: initialData?.featureFlags || "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onSubmit(formData);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Info */}
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">Test Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Login Flow Test"
              required
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              value={formData.description || ""}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Brief description of the test"
            />
          </div>
        </CardContent>
      </Card>

      {/* Test Prompt */}
      <Card>
        <CardHeader>
          <CardTitle>Test Prompt</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <Label htmlFor="prompt">
              Test Instructions (No Code Required) *
            </Label>
            <Textarea
              id="prompt"
              value={formData.prompt}
              onChange={(e) =>
                setFormData({ ...formData, prompt: e.target.value })
              }
              placeholder="Describe what you want to test in plain English. Example: 'Navigate to the login page, enter valid credentials, and verify successful login.'"
              className="min-h-[120px]"
              required
            />
            <p className="mt-2 text-xs text-gray-500">
              Write your test scenario in plain English. TestGPT will generate
              the actual test code using Playwright.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Network Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Network Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <Label htmlFor="networkMode">Network Mode</Label>
            <Select
              value={formData.networkMode}
              onValueChange={(value: any) =>
                setFormData({ ...formData, networkMode: value })
              }
            >
              <SelectTrigger id="networkMode">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="default">Default (No Throttling)</SelectItem>
                <SelectItem value="low">Low Bandwidth (3G)</SelectItem>
                <SelectItem value="high">High Bandwidth (4G/5G)</SelectItem>
              </SelectContent>
            </Select>
            <p className="mt-2 text-xs text-gray-500">
              Simulate different network conditions to test performance
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Device Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Device Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="deviceType">Device Type</Label>
            <Select
              value={formData.deviceType}
              onValueChange={(value: any) =>
                setFormData({ ...formData, deviceType: value })
              }
            >
              <SelectTrigger id="deviceType">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desktop">Desktop</SelectItem>
                <SelectItem value="android">Android</SelectItem>
                <SelectItem value="ios">iOS</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {formData.deviceType !== "desktop" && (
            <div>
              <Label htmlFor="deviceVersion">Device Version</Label>
              <Input
                id="deviceVersion"
                value={formData.deviceVersion || ""}
                onChange={(e) =>
                  setFormData({ ...formData, deviceVersion: e.target.value })
                }
                placeholder={
                  formData.deviceType === "android"
                    ? "e.g., Android 13"
                    : "e.g., iOS 17"
                }
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Screen Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Screen Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="aspectRatio">Aspect Ratio</Label>
            <Select
              value={formData.aspectRatio || undefined}
              onValueChange={(value) =>
                setFormData({ ...formData, aspectRatio: value })
              }
            >
              <SelectTrigger id="aspectRatio">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="16:9">16:9 (Widescreen)</SelectItem>
                <SelectItem value="16:10">16:10</SelectItem>
                <SelectItem value="4:3">4:3 (Standard)</SelectItem>
                <SelectItem value="21:9">21:9 (Ultrawide)</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="screenWidth">Screen Width (px)</Label>
              <Input
                id="screenWidth"
                type="number"
                value={formData.screenWidth ?? 1920}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    screenWidth: parseInt(e.target.value) || 1920,
                  })
                }
              />
            </div>
            <div>
              <Label htmlFor="screenHeight">Screen Height (px)</Label>
              <Input
                id="screenHeight"
                type="number"
                value={formData.screenHeight ?? 1080}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    screenHeight: parseInt(e.target.value) || 1080,
                  })
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Feature Flags */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Flags (Optional)</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <Label htmlFor="featureFlags">Feature Flags (JSON format)</Label>
            <Textarea
              id="featureFlags"
              value={formData.featureFlags || ""}
              onChange={(e) =>
                setFormData({ ...formData, featureFlags: e.target.value })
              }
              placeholder='{"newUI": true, "betaFeatures": false}'
              className="min-h-[80px] font-mono text-xs"
            />
            <p className="mt-2 text-xs text-gray-500">
              Optional: Specify feature flags as JSON to test specific feature
              configurations
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-end gap-4">
        <Button type="button" variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Test Configuration
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
