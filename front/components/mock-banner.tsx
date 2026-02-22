"use client";

import { isMockMode } from "@/lib/api";
import { Info } from "lucide-react";

export function MockBanner() {
  if (!isMockMode()) return null;
  return (
    <div className="border-b border-warning/30 bg-warning/10 px-4 py-2 text-center text-sm text-warning-foreground">
      <Info className="mr-1.5 inline-block size-4" />
      Demo mode — <code className="font-mono text-xs">NEXT_PUBLIC_API_BASE_URL</code> is not set. Showing mock data.
    </div>
  );
}
