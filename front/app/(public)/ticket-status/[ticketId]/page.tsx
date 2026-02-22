"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { PriorityBadge } from "@/components/priority-badge";
import { ArrowLeft } from "lucide-react";

type TicketDetails = {
  external_ticket_id: string;
  status: string;
  summary?: string;
  sentiment?: string;
  recommendation?: string;
  normalized_address?: string;
  ticket_type?: string;
  priority?: number | string;
  created_at?: string;
};

function mapPriority(value: number | string | undefined): string {
  if (typeof value === "string") {
    const upper = value.toUpperCase();
    if (["LOW", "MEDIUM", "HIGH", "URGENT"].includes(upper)) return upper;
  }
  const n = Number(value ?? 0);
  if (n >= 9) return "URGENT";
  if (n >= 7) return "HIGH";
  if (n >= 4) return "MEDIUM";
  return "LOW";
}

export default function TicketDetailsPage() {
  const params = useParams<{ ticketId: string }>();
  const ticketId = decodeURIComponent(String(params?.ticketId || ""));
  const [data, setData] = useState<TicketDetails | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setError(null);
      try {
        const item = await apiFetch<Record<string, unknown>>(
          `/api/v1/tickets/by-external/${encodeURIComponent(ticketId)}`
        );
        setData({
          external_ticket_id: String(item.external_ticket_id || ticketId),
          status: String(item.status || "DONE"),
          summary: String(item.summary || ""),
          sentiment: String(item.sentiment || ""),
          recommendation: String(item.recommendation || ""),
          normalized_address: String(item.normalized_address || ""),
          ticket_type: String(item.ticket_type || ""),
          priority: (item.priority as number | string | undefined) ?? "",
          created_at: String(item.created_at || ""),
        });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load ticket details");
      }
    }
    if (ticketId) load();
  }, [ticketId]);

  const priorityLabel = useMemo(() => mapPriority(data?.priority), [data?.priority]);

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-10 sm:px-6">
      <div className="flex items-center justify-between">
        <Link href="/ticket-status" className="inline-flex items-center text-sm text-primary hover:underline">
          <ArrowLeft className="mr-1 size-4" />
          Back to status search
        </Link>
      </div>

      {error && (
        <Card>
          <CardContent className="py-6 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {data && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="font-mono text-xl">{data.external_ticket_id}</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center gap-3">
              <StatusBadge status={data.status} />
              <PriorityBadge priority={priorityLabel} />
              <Badge variant="outline">{data.ticket_type || "N/A"}</Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent className="text-sm">{data.summary || "N/A"}</CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sentiment</CardTitle>
            </CardHeader>
            <CardContent className="text-sm">{data.sentiment || "N/A"}</CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recommendation</CardTitle>
            </CardHeader>
            <CardContent className="whitespace-pre-wrap text-sm">{data.recommendation || "N/A"}</CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Normalized Address</CardTitle>
            </CardHeader>
            <CardContent className="text-sm">{data.normalized_address || "N/A"}</CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
