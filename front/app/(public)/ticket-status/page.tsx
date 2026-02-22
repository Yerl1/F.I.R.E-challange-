"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Search, Clock } from "lucide-react";
import { apiFetch, isMockMode } from "@/lib/api";
import { MOCK_TICKET_STATUS } from "@/lib/mock-data";
import { TicketOfficeManagerPanel } from "@/components/ticket-office-manager-panel";
import { StatusBadge } from "@/components/status-badge";
import { ApiErrorCallout } from "@/components/api-error-callout";
import type { TicketStatusResponse } from "@/lib/types";
import { format } from "date-fns";

export default function TicketStatusPage() {
  const [ticketId, setTicketId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TicketStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!ticketId.trim()) {
      toast.error("Please enter a ticket ID.");
      return;
    }
    setIsLoading(true);
    setResult(null);
    setError(null);
    try {
      let res: TicketStatusResponse;
      if (isMockMode()) {
        await new Promise((r) => setTimeout(r, 800));
        res = { ...MOCK_TICKET_STATUS, ticket_id: ticketId.trim() };
      } else {
        const item = await apiFetch<Record<string, unknown>>(
          `/api/v1/tickets/by-external/${encodeURIComponent(ticketId.trim())}`
        );
        res = {
          ticket_id: String(item.external_ticket_id || ticketId.trim()),
          status: String(item.status || "DONE"),
          created_at: String(item.created_at || ""),
          office: item.office_name
            ? {
                name: String(item.office_name),
                address: String(item.office_address || ""),
                city: String(item.city || ""),
              }
            : undefined,
          manager: item.manager_name
            ? {
                full_name: String(item.manager_name),
                role: "Assigned manager",
              }
            : undefined,
          summary: String(item.summary || ""),
          request_type: String(item.ticket_type || ""),
          priority: String(item.priority || ""),
        };
      }
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ticket not found");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Ticket Status
        </h1>
        <p className="mt-1 text-muted-foreground">
          Enter your ticket ID to check the current status
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Find Your Ticket</CardTitle>
          <CardDescription>
            Enter the ticket ID you received when creating your request
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="flex-1 space-y-2">
              <Label htmlFor="ticket_id" className="sr-only">
                Ticket ID
              </Label>
              <Input
                id="ticket_id"
                placeholder="e.g., TK-001"
                value={ticketId}
                onChange={(e) => setTicketId(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <>
                  <Search className="mr-2 size-4" />
                  Find
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && <ApiErrorCallout message={error} />}

      {result && (
        <div className="space-y-6">
          <div className="flex items-center justify-between rounded-lg border border-border bg-card p-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">
                Ticket{" "}
                <Link
                  href={`/ticket-status/${encodeURIComponent(result.ticket_id)}`}
                  className="font-mono font-medium text-primary hover:underline"
                >
                  {result.ticket_id}
                </Link>
              </p>
              {result.created_at && (
                <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="size-3.5" />
                  Created {format(new Date(result.created_at), "MMM d, yyyy 'at' h:mm a")}
                </p>
              )}
            </div>
            <StatusBadge status={result.status} />
          </div>

          {result.status === "PROCESSING" && (
            <Card>
              <CardContent className="flex flex-col items-center py-10 text-center">
                <Loader2 className="mb-4 size-8 animate-spin text-primary" />
                <p className="font-medium text-foreground">
                  Your request is still being processed
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Please check back in a moment. Our system is analyzing your request and finding the best match.
                </p>
              </CardContent>
            </Card>
          )}

          {result.status !== "PROCESSING" && result.office && result.manager && (
            <TicketOfficeManagerPanel
              ticketId={result.ticket_id}
              office={result.office}
              manager={result.manager}
            />
          )}
        </div>
      )}
    </div>
  );
}
