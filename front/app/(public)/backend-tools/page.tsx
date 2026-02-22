"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiFetch, apiUploadFetch, isMockMode } from "@/lib/api";
import type {
  BackendBootstrapResponse,
  BackendProcessCsvResponse,
  BackendProcessOneResponse,
  BackendRecentResponse,
  HealthResponse,
} from "@/lib/types";

const SAMPLE_ONE = {
  payload: {
    ticket_id: "WEB-1",
    raw_text: "Здравствуйте, приложение не открывается после обновления.",
    segment: "retail",
    country: "KZ",
    region: "Алматинская область",
    city: "Алматы",
    street: "Абая",
    house: "10",
    attachments: "",
  },
};

export default function BackendToolsPage() {
  const [csvPath, setCsvPath] = useState("docs/tickets.csv");
  const [singlePayload, setSinglePayload] = useState(JSON.stringify(SAMPLE_ONE, null, 2));
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run<T>(fn: () => Promise<T>) {
    setLoading(true);
    setError(null);
    try {
      const data = await fn();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function ensureApiConfigured() {
    if (isMockMode()) {
      setError("Set NEXT_PUBLIC_API_BASE_URL to backend URL, for example http://localhost:8001");
      return false;
    }
    return true;
  }

  async function onBootstrap() {
    if (!ensureApiConfigured()) return;
    await run(() => apiFetch<BackendBootstrapResponse>("/api/v1/bootstrap", { method: "POST" }));
  }

  async function onHealth() {
    if (!ensureApiConfigured()) return;
    await run(() => apiFetch<HealthResponse>("/health"));
  }

  async function onRecent() {
    if (!ensureApiConfigured()) return;
    await run(() => apiFetch<BackendRecentResponse>("/api/v1/tickets/recent?limit=20"));
  }

  async function onProcessCsvPath(e: FormEvent) {
    e.preventDefault();
    if (!ensureApiConfigured()) return;
    await run(() =>
      apiFetch<BackendProcessCsvResponse>("/api/v1/tickets/process-csv", {
        method: "POST",
        body: { csv_path: csvPath },
      })
    );
  }

  async function onProcessCsvUpload(e: FormEvent) {
    e.preventDefault();
    if (!ensureApiConfigured()) return;
    if (!csvFile) {
      setError("Select a CSV file first");
      return;
    }
    await run(() => apiUploadFetch<BackendProcessCsvResponse>("/api/v1/tickets/process-csv-upload", csvFile));
  }

  async function onProcessOne(e: FormEvent) {
    e.preventDefault();
    if (!ensureApiConfigured()) return;
    let parsed: unknown;
    try {
      parsed = JSON.parse(singlePayload);
    } catch {
      setError("Invalid JSON in single ticket payload");
      return;
    }

    await run(() =>
      apiFetch<BackendProcessOneResponse>("/api/v1/tickets/process-one", {
        method: "POST",
        body: parsed,
      })
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-8 sm:px-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Backend Tools</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Проверка health/bootstrap, запуск обработки одного тикета и CSV (по пути или upload).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button onClick={onHealth} disabled={loading}>
            Health
          </Button>
          <Button onClick={onBootstrap} disabled={loading} variant="secondary">
            Bootstrap refs
          </Button>
          <Button onClick={onRecent} disabled={loading} variant="outline">
            Recent tickets
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Process CSV by path</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onProcessCsvPath} className="space-y-3">
            <Label htmlFor="csv-path">CSV path on backend host</Label>
            <Input
              id="csv-path"
              value={csvPath}
              onChange={(e) => setCsvPath(e.target.value)}
              placeholder="docs/tickets.csv"
            />
            <Button type="submit" disabled={loading}>
              Run process-csv
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Process CSV upload</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onProcessCsvUpload} className="space-y-3">
            <Input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setCsvFile(e.target.files?.[0] ?? null)}
            />
            <Button type="submit" disabled={loading}>
              Upload and process
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Process one ticket</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onProcessOne} className="space-y-3">
            <Textarea
              value={singlePayload}
              onChange={(e) => setSinglePayload(e.target.value)}
              rows={14}
              className="font-mono text-xs"
            />
            <Button type="submit" disabled={loading}>
              Run process-one
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm text-destructive">{error}</pre>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Response</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="max-h-[500px] overflow-auto rounded-md bg-muted p-3 text-xs">
            {result ? JSON.stringify(result, null, 2) : "No response yet"}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
