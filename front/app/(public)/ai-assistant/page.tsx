"use client";

import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, Bot, Loader2, Send, Sparkles, User } from "lucide-react";
import { AssistantChart } from "@/components/assistant-chart";
import { AssistantTable } from "@/components/assistant-table";

type ChartKind = "bar" | "line" | "pie" | "area";

type ChartData = {
  chartType: ChartKind;
  title: string;
  xAxisLabel: string | null;
  yAxisLabel: string | null;
  data: { label: string; value: number; value2: number | null }[];
  series1Name: string;
  series2Name: string | null;
};

type TableData = {
  title: string;
  columns: string[];
  rows: string[][];
};

type AnalyticsResponse = {
  request_id: string;
  dsl: Record<string, unknown>;
  sql: string;
  data: Array<Record<string, unknown>>;
  chart_spec: Record<string, unknown>;
  summary: string;
};

type ChatItem = {
  id: string;
  role: "user" | "assistant";
  text: string;
  analytics?: AnalyticsResponse;
  error?: string;
};

const SUGGESTIONS = [
  "Покажи распределение типов обращений по городам за 30 дней",
  "Топ-10 городов по количеству обращений",
  "Сравни тональность обращений по сегментам",
  "Покажи тренд обращений по дням за последние 2 недели",
];

function toStringSafe(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  return String(value);
}

function toNumberSafe(value: unknown, fallback = 0): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeChartType(dsl: Record<string, unknown>, chartSpec: Record<string, unknown>): ChartKind {
  const dslType = toStringSafe((dsl.chart as Record<string, unknown> | undefined)?.type, "").toLowerCase();
  const markRaw = chartSpec.mark;
  const mark = typeof markRaw === "string" ? markRaw.toLowerCase() : toStringSafe((markRaw as Record<string, unknown> | undefined)?.type, "").toLowerCase();

  const source = `${dslType} ${mark}`;
  if (source.includes("line")) return "line";
  if (source.includes("pie")) return "pie";
  if (source.includes("area")) return "area";
  return "bar";
}

function getXFields(dsl: Record<string, unknown>, chartSpec: Record<string, unknown>): string[] {
  const dims = Array.isArray(dsl.dimensions) ? dsl.dimensions.map((v) => toStringSafe(v)).filter(Boolean) : [];
  if (dims.length > 0) return dims;

  const encoding = (chartSpec.encoding as Record<string, unknown> | undefined) ?? {};
  const xField = toStringSafe((encoding.x as Record<string, unknown> | undefined)?.field, "");
  if (!xField) return [];
  return xField
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

function getYField(dsl: Record<string, unknown>, chartSpec: Record<string, unknown>): string {
  const dslChart = (dsl.chart as Record<string, unknown> | undefined) ?? {};
  const chartY = toStringSafe(dslChart.y, "");
  if (chartY) return chartY;

  const metrics = Array.isArray(dsl.metrics) ? dsl.metrics : [];
  if (metrics.length > 0) {
    const alias = toStringSafe((metrics[0] as Record<string, unknown>).as, "");
    if (alias) return alias;
  }

  const encoding = (chartSpec.encoding as Record<string, unknown> | undefined) ?? {};
  const yField = toStringSafe((encoding.y as Record<string, unknown> | undefined)?.field, "");
  return yField || "tickets";
}

function mapAnalyticsToChart(resp: AnalyticsResponse): ChartData {
  const chartType = normalizeChartType(resp.dsl, resp.chart_spec);
  const xFields = getXFields(resp.dsl, resp.chart_spec);
  const yField = getYField(resp.dsl, resp.chart_spec);

  const points = (resp.data || []).map((row) => {
    const label =
      xFields.length > 0
        ? xFields.map((field) => toStringSafe(row[field], "unknown")).join(" / ")
        : toStringSafe(row.city ?? row.ticket_type ?? row.segment ?? "unknown");

    return {
      label,
      value: toNumberSafe(row[yField], 0),
      value2: null,
    };
  });

  return {
    chartType,
    title: toStringSafe(resp.summary, "Analytics Result"),
    xAxisLabel: xFields.length > 0 ? xFields.join(", ") : null,
    yAxisLabel: yField,
    data: points,
    series1Name: yField,
    series2Name: null,
  };
}

function mapAnalyticsToTable(resp: AnalyticsResponse): TableData | null {
  if (!resp.data || resp.data.length === 0) return null;
  const columns = Object.keys(resp.data[0]);
  if (columns.length === 0) return null;

  const rows = resp.data.slice(0, 20).map((row) => columns.map((column) => toStringSafe(row[column])));
  return {
    title: "SQL Result Preview",
    columns,
    rows,
  };
}

export default function AiAssistantPage() {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatItem[]>([]);

  const apiBase = useMemo(() => process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001", []);

  async function submitQuery(text: string): Promise<void> {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const userMsg: ChatItem = {
      id: `u-${Date.now()}`,
      role: "user",
      text: trimmed,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBase}/api/v1/analytics/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmed }),
      });
      const payload = (await response.json()) as AnalyticsResponse | { detail?: unknown };

      if (!response.ok) {
        const detail = (payload as { detail?: unknown }).detail;
        const errorText = typeof detail === "string" ? detail : JSON.stringify(detail);
        throw new Error(errorText || `HTTP ${response.status}`);
      }

      const assistantMsg: ChatItem = {
        id: `a-${Date.now()}`,
        role: "assistant",
        text: (payload as AnalyticsResponse).summary || "Готово.",
        analytics: payload as AnalyticsResponse,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      const assistantMsg: ChatItem = {
        id: `e-${Date.now()}`,
        role: "assistant",
        text: "Не удалось получить ответ от AI аналитики.",
        error: toStringSafe((error as Error)?.message, "Unknown error"),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setIsLoading(false);
    }
  }

  function onSubmit(event: React.FormEvent): void {
    event.preventDefault();
    void submitQuery(input);
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-xl bg-primary/10">
          <Sparkles className="size-6 text-primary" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">AI Assistant</h1>
        <p className="mt-1 text-sm text-muted-foreground">Natural language analytics via backend AI agent</p>
      </div>

      <Card className="flex h-[calc(100vh-16rem)] flex-col overflow-hidden border-border">
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="grid gap-2">
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => {
                    void submitQuery(suggestion);
                  }}
                  className="rounded-lg border border-border bg-card px-3 py-2.5 text-left text-xs text-muted-foreground transition-colors hover:border-primary/30 hover:bg-accent hover:text-foreground"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => {
                const chart = message.analytics ? mapAnalyticsToChart(message.analytics) : null;
                const table = message.analytics ? mapAnalyticsToTable(message.analytics) : null;

                return (
                  <div key={message.id} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
                    <div className={message.role === "user" ? "flex max-w-[85%] gap-2.5" : "flex max-w-[95%] gap-2.5"}>
                      {message.role === "assistant" && (
                        <div className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
                          <Bot className="size-4 text-primary" />
                        </div>
                      )}

                      <div className="min-w-0 flex-1 space-y-2">
                        <div
                          className={
                            message.role === "user"
                              ? "rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm text-primary-foreground"
                              : "text-sm leading-relaxed text-foreground whitespace-pre-wrap"
                          }
                        >
                          {message.text}
                        </div>

                        {message.error && (
                          <div className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
                            <div className="mb-1 flex items-center gap-1.5 font-medium">
                              <AlertCircle className="size-3.5" />
                              Backend error
                            </div>
                            {message.error}
                          </div>
                        )}

                        {chart && chart.data.length > 0 && <AssistantChart data={chart} />}
                        {table && <AssistantTable data={table} />}

                        {message.analytics && (
                          <details className="rounded-md border border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
                            <summary className="cursor-pointer select-none">Debug payload</summary>
                            <pre className="mt-2 max-h-60 overflow-auto whitespace-pre-wrap break-words">
                              {JSON.stringify(
                                {
                                  request_id: message.analytics.request_id,
                                  dsl: message.analytics.dsl,
                                  sql: message.analytics.sql,
                                },
                                null,
                                2
                              )}
                            </pre>
                          </details>
                        )}
                      </div>

                      {message.role === "user" && (
                        <div className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                          <User className="size-4 text-muted-foreground" />
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex gap-2.5">
                    <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <Bot className="size-4 text-primary" />
                    </div>
                    <div className="flex items-center gap-1.5 rounded-2xl bg-muted px-4 py-2.5">
                      <Loader2 className="size-3.5 animate-spin text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="border-t border-border bg-card p-4">
          <form onSubmit={onSubmit} className="flex gap-2">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask for analytics, for example: Покажи распределение типов обращений по городам"
              className="min-h-[44px] max-h-32 flex-1 resize-none text-sm"
              rows={1}
              disabled={isLoading}
            />
            <Button type="submit" size="icon" disabled={!input.trim() || isLoading} className="size-11 shrink-0">
              {isLoading ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}

