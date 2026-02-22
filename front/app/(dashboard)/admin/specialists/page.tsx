"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Users } from "lucide-react";
import { apiFetch, isMockMode } from "@/lib/api";

type ManagerItem = {
  id: number | string;
  full_name: string;
  position: string;
  office_id: number | string;
  active_tickets: number;
  assignments_total: number;
};

export default function AdminSpecialistsPage() {
  const [managers, setManagers] = useState<ManagerItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadManagers() {
      setIsLoading(true);
      try {
        if (isMockMode()) {
          setManagers([]);
          return;
        }
        const res = await apiFetch<{ items: Record<string, unknown>[] }>("/api/v1/managers");
        setManagers(
          (res.items || []).map((item) => ({
            id: String(item.id || ""),
            full_name: String(item.full_name || ""),
            position: String(item.position || ""),
            office_id: String(item.office_id || ""),
            active_tickets: Number(item.active_tickets || 0),
            assignments_total: Number(item.assignments_total || 0),
          }))
        );
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Failed to load managers");
      } finally {
        setIsLoading(false);
      }
    }
    loadManagers();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Specialists
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Specialists (managers) from backend reference data.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="size-5" />
            Specialist List
          </CardTitle>
          <CardDescription>Assignments and current workload.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Loading...</div>
          ) : (
            <div className="rounded-lg border border-border">
              <Table>
                <TableHeader>
                  <TableRow className="bg-muted/30 hover:bg-muted/30">
                    <TableHead>ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Position</TableHead>
                    <TableHead>Office ID</TableHead>
                    <TableHead>Active</TableHead>
                    <TableHead>Total Assigned</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {managers.map((m) => (
                    <TableRow key={String(m.id)}>
                      <TableCell className="font-mono text-xs">{m.id}</TableCell>
                      <TableCell className="font-medium">{m.full_name}</TableCell>
                      <TableCell>{m.position}</TableCell>
                      <TableCell>{m.office_id}</TableCell>
                      <TableCell>{m.active_tickets}</TableCell>
                      <TableCell>{m.assignments_total}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
