"use client";

import { useState, useEffect, useMemo } from "react";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TicketTable } from "@/components/ticket-table";
import { apiFetch, isMockMode } from "@/lib/api";
import { MOCK_TICKETS } from "@/lib/mock-data";
import type { TicketListItem } from "@/lib/types";
import { Search } from "lucide-react";

function mapPriority(value: number | string): string {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(n)) return "MEDIUM";
  if (n >= 9) return "URGENT";
  if (n >= 7) return "HIGH";
  if (n >= 4) return "MEDIUM";
  return "LOW";
}

export default function SpecialistTicketsPage() {
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [cityFilter, setCityFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");

  useEffect(() => {
    async function load() {
      try {
        let data: TicketListItem[];
        if (isMockMode()) {
          await new Promise((r) => setTimeout(r, 600));
          data = MOCK_TICKETS;
        } else {
          const recent = await apiFetch<{ items: Record<string, unknown>[] }>(
            "/api/v1/tickets/recent?limit=200"
          );
          data = (recent.items || []).map((item) => ({
            ticket_id: String(item.external_ticket_id || item.id || ""),
            created_at: String(item.created_at || new Date().toISOString()),
            status: String(item.status || "DONE"),
            summary: String(item.summary || ""),
            city: String(item.city || ""),
            request_type: String(item.ticket_type || ""),
            priority: mapPriority(item.priority as number | string),
          }));
        }
        setTickets(data);
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Failed to load tickets");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const cities = useMemo(
    () => [...new Set(tickets.map((t) => t.city))],
    [tickets]
  );
  const types = useMemo(
    () => [...new Set(tickets.map((t) => t.request_type))],
    [tickets]
  );

  const filtered = useMemo(() => {
    return tickets.filter((t) => {
      const s = search.toLowerCase();
      if (s && !t.ticket_id.toLowerCase().includes(s) && !t.summary.toLowerCase().includes(s)) {
        return false;
      }
      if (statusFilter !== "all" && t.status !== statusFilter) return false;
      if (cityFilter !== "all" && t.city !== cityFilter) return false;
      if (typeFilter !== "all" && t.request_type !== typeFilter) return false;
      if (priorityFilter !== "all" && t.priority !== priorityFilter) return false;
      return true;
    });
  }, [tickets, search, statusFilter, cityFilter, typeFilter, priorityFilter]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Assigned Tickets
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          View and manage tickets assigned to you
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by ID or summary..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="PROCESSING">Processing</SelectItem>
            <SelectItem value="DONE">Done</SelectItem>
            <SelectItem value="ERROR">Error</SelectItem>
          </SelectContent>
        </Select>
        <Select value={cityFilter} onValueChange={setCityFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="City" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Cities</SelectItem>
            {cities.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {types.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="URGENT">Urgent</SelectItem>
            <SelectItem value="HIGH">High</SelectItem>
            <SelectItem value="MEDIUM">Medium</SelectItem>
            <SelectItem value="LOW">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <TicketTable tickets={filtered} isLoading={isLoading} />
    </div>
  );
}
