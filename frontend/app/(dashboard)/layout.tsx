import { Navigation } from "@/components/navigation";
import { Suspense } from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section className="flex min-h-screen flex-col">
      <Suspense
        fallback={
          <div className="h-16 w-full border-b border-gray-200 bg-white" />
        }
      >
        <Navigation />
      </Suspense>
      <main className="flex-1 bg-gray-50">{children}</main>
    </section>
  );
}
