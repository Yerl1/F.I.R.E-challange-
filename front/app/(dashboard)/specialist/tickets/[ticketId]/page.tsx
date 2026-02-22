"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/status-badge";
import { PriorityBadge } from "@/components/priority-badge";
import { ChatPanel } from "@/components/chat-panel";
import { ApiErrorCallout } from "@/components/api-error-callout";
import { apiFetch, isMockMode } from "@/lib/api";
import { MOCK_TICKET_DETAIL } from "@/lib/mock-data";
import type { TicketDetail } from "@/lib/types";
import { ArrowLeft, Clock, MapPin, FileText, Brain, Route } from "lucide-react";
import { format } from "date-fns";

export default function TicketDetailPage({
  params,
}: {
  params: Promise<{ ticketId: string }>;
}) {
  const { ticketId } = use(params);
  const router = useRouter();
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisOpen, setAnalysisOpen] = useState(false);

  function mapPriority(value: number | string): string {
    const n = typeof value === "number" ? value : Number(value);
    if (!Number.isFinite(n)) return "MEDIUM";
    if (n >= 9) return "URGENT";
    if (n >= 7) return "HIGH";
    if (n >= 4) return "MEDIUM";
    return "LOW";
  }

  useEffect(() => {
    async function load() {
      try {
        let data: TicketDetail;
        if (isMockMode()) {
          await new Promise((r) => setTimeout(r, 500));
          data = { ...MOCK_TICKET_DETAIL, ticket_id: ticketId };
        } else {
          const item = await apiFetch<Record<string, unknown>>(
            `/api/v1/tickets/by-external/${encodeURIComponent(ticketId)}`
          );
          data = {
            ticket_id: String(item.external_ticket_id || ticketId),
            created_at: String(item.created_at || ""),
            status: String(item.status || "DONE"),
            summary: String(item.summary || ""),
            city: String(item.city || ""),
            request_type: String(item.ticket_type || ""),
            priority: mapPriority(item.priority as number | string),
            raw_text: String(item.raw_text || ""),
            ai_analysis: (item.payload as Record<string, unknown>) || undefined,
            assignment_reason: String(item.recommendation || ""),
          };
        }
        setTicket(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ticket not found");
        toast.error("Failed to load ticket");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [ticketId]);

  if (isLoading) {
    return <TicketDetailSkeleton />;
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 size-4" />
          Back
        </Button>
        <ApiErrorCallout message={error} />
      </div>
    );
  }

  if (!ticket) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 size-4" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-xl font-semibold text-foreground font-mono">
            {ticket.ticket_id}
          </h1>
          {ticket.created_at && (
            <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
              <Clock className="size-3.5" />
              {format(new Date(ticket.created_at), "MMMM d, yyyy 'at' h:mm a")}
            </p>
          )}
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Left: Ticket Info */}
        <div className="space-y-6 lg:col-span-3">
          {/* Meta tags */}
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={ticket.status} />
            <PriorityBadge priority={ticket.priority} />
            {ticket.city && (
              <span className="flex items-center gap-1 rounded-md border border-border bg-card px-2.5 py-0.5 text-xs text-muted-foreground">
                <MapPin className="size-3" />
                {ticket.city}
              </span>
            )}
            {ticket.request_type && (
              <span className="rounded-md border border-border bg-card px-2.5 py-0.5 text-xs text-muted-foreground">
                {ticket.request_type}
              </span>
            )}
          </div>

          {/* Raw Text */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <FileText className="size-4" />
                Customer Request
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground">
                {ticket.raw_text}
              </pre>
            </CardContent>
          </Card>

          {/* AI Analysis */}
          {ticket.ai_analysis && (
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Brain className="size-4" />
                    AI Analysis
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setAnalysisOpen(!analysisOpen)}
                  >
                    {analysisOpen ? "Collapse" : "Expand"}
                  </Button>
                </div>
              </CardHeader>
              {analysisOpen && (
                <CardContent>
                  <pre className="overflow-auto rounded-md bg-muted p-3 font-mono text-xs leading-relaxed text-foreground">
                    {JSON.stringify(ticket.ai_analysis, null, 2)}
                  </pre>
                </CardContent>
              )}
            </Card>
          )}

          {/* Assignment Reason */}
          {ticket.assignment_reason && (
            <Card className="border-primary/20 bg-primary/[0.02]">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm font-medium text-primary">
                  <Route className="size-4" />
                  Assignment Reason
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-foreground">
                  {ticket.assignment_reason}
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right: Chat */}
        <div className="lg:col-span-2">
          <ChatPanel ticketId={ticketId} />
        </div>
      </div>
    </div>
  );
}

function TicketDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-8 w-20" />
        <div>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="mt-1 h-4 w-48" />
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          <Skeleton className="h-40 w-full rounded-lg" />
          <Skeleton className="h-32 w-full rounded-lg" />
        </div>
        <div className="lg:col-span-2">
          <Skeleton className="h-80 w-full rounded-lg" />
        </div>
      </div>
    </div>
  );
}
