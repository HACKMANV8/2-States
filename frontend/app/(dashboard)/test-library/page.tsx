import { Suspense } from "react";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import {
  PlayCircle,
  Eye,
  Edit,
  Trash2,
  Clock,
  Globe,
  Tag,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export const dynamic = "force-dynamic";

async function getTestSuites() {
  try {
    return await apiClient.listTestSuites({ limit: 100 });
  } catch (error) {
    console.error("Failed to fetch test suites:", error);
    return [];
  }
}

export default async function TestLibraryPage() {
  const testSuites = await getTestSuites();

  return (
    <div className="mx-auto max-w-7xl p-6">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Test Library</h1>
          <p className="mt-2 text-gray-500">
            Manage and run your saved test suites
          </p>
        </div>
        <Link href="/test-config">
          <Button>
            <PlayCircle className="mr-2 h-4 w-4" />
            Create New Test
          </Button>
        </Link>
      </div>

      {testSuites.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Globe className="mb-4 h-12 w-12 text-gray-400" />
            <h3 className="mb-2 text-lg font-semibold">No test suites yet</h3>
            <p className="mb-6 text-sm text-gray-500">
              Create your first test suite to get started
            </p>
            <Link href="/test-config">
              <Button>Create Test Suite</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {testSuites.map((suite) => (
            <Card
              key={suite.id}
              className="transition-shadow hover:shadow-md"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{suite.name}</CardTitle>
                    <CardDescription className="mt-1 flex items-center gap-1">
                      <Globe className="h-3 w-3" />
                      <span className="truncate">{suite.target_url}</span>
                    </CardDescription>
                  </div>
                </div>

                {suite.description && (
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                    {suite.description}
                  </p>
                )}
              </CardHeader>

              <CardContent>
                <div className="space-y-3">
                  {/* Tags */}
                  {suite.tags && suite.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {suite.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          <Tag className="mr-1 h-3 w-3" />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="space-y-1 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>
                        Created{" "}
                        {formatDistanceToNow(new Date(suite.created_at), {
                          addSuffix: true,
                        })}
                      </span>
                    </div>
                    {suite.last_run && (
                      <div className="flex items-center gap-1">
                        <PlayCircle className="h-3 w-3" />
                        <span>
                          Last run{" "}
                          {formatDistanceToNow(new Date(suite.last_run), {
                            addSuffix: true,
                          })}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Link href={`/test-library/${suite.id}`} className="flex-1">
                      <Button variant="outline" size="sm" className="w-full">
                        <Eye className="mr-1 h-3 w-3" />
                        View
                      </Button>
                    </Link>
                    <Link href={`/test-library/${suite.id}/run`}>
                      <Button size="sm">
                        <PlayCircle className="mr-1 h-3 w-3" />
                        Run
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
