"use client";

import Link from "next/link";
import { format } from "date-fns";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/status-badge";
import { PriorityBadge } from "@/components/priority-badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { TicketListItem } from "@/lib/types";

export function TicketTable({
  tickets,
  isLoading,
}: {
  tickets: TicketListItem[];
  isLoading: boolean;
}) {
  if (isLoading) {
    return <TicketTableSkeleton />;
  }

  if (tickets.length === 0) {
    return (
      <div className="flex flex-col items-center py-16 text-center">
        <p className="text-sm text-muted-foreground">No tickets found</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/30 hover:bg-muted/30">
            <TableHead className="w-28">Ticket ID</TableHead>
            <TableHead className="w-36">Created</TableHead>
            <TableHead className="w-28">Status</TableHead>
            <TableHead className="w-28">City</TableHead>
            <TableHead className="w-32">Type</TableHead>
            <TableHead className="w-24">Priority</TableHead>
            <TableHead>Summary</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((t) => (
            <TableRow key={t.ticket_id} className="group cursor-pointer">
              <TableCell>
                <Link
                  href={`/specialist/tickets/${t.ticket_id}`}
                  className="font-mono text-sm font-medium text-primary hover:underline"
                >
                  {t.ticket_id}
                </Link>
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {format(new Date(t.created_at), "MMM d, h:mm a")}
              </TableCell>
              <TableCell>
                <StatusBadge status={t.status} />
              </TableCell>
              <TableCell className="text-sm">{t.city}</TableCell>
              <TableCell className="text-sm">{t.request_type}</TableCell>
              <TableCell>
                <PriorityBadge priority={t.priority} />
              </TableCell>
              <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                {t.summary}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function TicketTableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-lg border border-border p-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-4 flex-1" />
        </div>
      ))}
    </div>
  );
}
