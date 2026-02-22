"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2, Building2, Database } from "lucide-react";
import { apiFetch, isMockMode } from "@/lib/api";
import { MOCK_OFFICES } from "@/lib/mock-data";
import type { Office } from "@/lib/types";

type OfficeItem = Office & { id?: string | number };

export default function AdminOfficesPage() {
  const [offices, setOffices] = useState<OfficeItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isBootstrapping, setIsBootstrapping] = useState(false);

  async function loadOffices() {
    setIsLoading(true);
    try {
      if (isMockMode()) {
        setOffices(MOCK_OFFICES);
      } else {
        const res = await apiFetch<{ items: Record<string, unknown>[] }>("/api/v1/offices");
        setOffices(
          (res.items || []).map((item) => ({
            id: String(item.id || ""),
            name: String(item.name || ""),
            address: String(item.address || ""),
            city: "",
          }))
        );
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load offices");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadOffices();
  }, []);

  async function handleBootstrap() {
    if (isMockMode()) {
      toast.success("Mock mode: bootstrap skipped");
      return;
    }
    setIsBootstrapping(true);
    try {
      const stats = await apiFetch<{ offices: number; managers: number }>("/api/v1/bootstrap", {
        method: "POST",
      });
      toast.success(`Bootstrap done: offices=${stats.offices}, managers=${stats.managers}`);
      await loadOffices();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Bootstrap failed");
    } finally {
      setIsBootstrapping(false);
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Offices
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Offices are loaded from backend reference data.
          </p>
        </div>
        <Button onClick={handleBootstrap} disabled={isBootstrapping}>
          {isBootstrapping ? (
            <Loader2 className="mr-2 size-4 animate-spin" />
          ) : (
            <Database className="mr-2 size-4" />
          )}
          Bootstrap refs
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="size-5" />
            Office List
          </CardTitle>
          <CardDescription>Current backend offices.</CardDescription>
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
                    <TableHead>Address</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {offices.map((o) => (
                    <TableRow key={String(o.id || o.name)}>
                      <TableCell className="font-mono text-xs">{o.id}</TableCell>
                      <TableCell className="font-medium">{o.name}</TableCell>
                      <TableCell className="text-muted-foreground">{o.address}</TableCell>
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
