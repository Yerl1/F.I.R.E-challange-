"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiErrorCallout } from "@/components/api-error-callout";
import { apiFetch, isMockMode } from "@/lib/api";
import { MOCK_HEALTH } from "@/lib/mock-data";
import type { HealthResponse } from "@/lib/types";
import { Activity, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

export default function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadHealth() {
    setIsLoading(true);
    setError(null);
    try {
      let data: HealthResponse;
      if (isMockMode()) {
        await new Promise((r) => setTimeout(r, 500));
        data = MOCK_HEALTH;
      } else {
        data = await apiFetch<HealthResponse>("/health");
      }
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Health check failed");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            System Health
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Backend service status and diagnostics
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadHealth} disabled={isLoading}>
          <RefreshCw className={`mr-2 size-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && <ApiErrorCallout message={error} />}

      {isLoading && !health && (
        <Card>
          <CardContent className="space-y-3 py-6">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </CardContent>
        </Card>
      )}

      {health && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="size-5 text-primary" />
              Service Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="size-6 text-success" />
              <div>
                <p className="font-semibold text-foreground">
                  Status: {health.status}
                </p>
              </div>
              <Badge className="ml-auto bg-success text-success-foreground border-transparent">
                Operational
              </Badge>
            </div>

            <div className="rounded-lg border border-border bg-muted/30 p-4">
              <pre className="font-mono text-sm leading-relaxed text-foreground">
                {JSON.stringify(health, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
