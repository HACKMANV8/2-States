import { TestConfigForm } from "@/components/test-config/test-config-form";
import { redirect } from "next/navigation";
import { db } from "@/lib/db/client";
import { testConfigurations } from "@/lib/db/schema";

export const dynamic = "force-dynamic";

export default function TestConfigPage() {
  async function createTestConfig(formData: FormData) {
    "use server";

    const data = {
      name: formData.get("name") as string,
      description: (formData.get("description") as string) || null,
      prompt: formData.get("prompt") as string,
      networkMode: (formData.get("networkMode") as any) || "default",
      deviceType: (formData.get("deviceType") as any) || "desktop",
      deviceVersion: (formData.get("deviceVersion") as string) || null,
      screenWidth: parseInt(formData.get("screenWidth") as string) || 1920,
      screenHeight: parseInt(formData.get("screenHeight") as string) || 1080,
      aspectRatio: (formData.get("aspectRatio") as string) || "16:9",
      featureFlags: (formData.get("featureFlags") as string) || null,
    };

    const [result] = await db
      .insert(testConfigurations)
      .values(data)
      .returning();

    redirect(`/test-executions`);
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Create Test Configuration
        </h1>
        <p className="mt-2 text-gray-500">
          Configure your test parameters and write test prompts without code
        </p>
      </div>

      <TestConfigForm
        onSubmit={async (data) => {
          "use server";
          await db.insert(testConfigurations).values(data as any);
          redirect("/test-executions");
        }}
      />
    </div>
  );
}
