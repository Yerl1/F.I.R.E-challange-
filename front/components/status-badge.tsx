import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusConfig: Record<string, { className: string; label: string }> = {
  PROCESSING: {
    className: "bg-warning text-warning-foreground border-transparent",
    label: "Processing",
  },
  DONE: {
    className: "bg-success text-success-foreground border-transparent",
    label: "Done",
  },
  ERROR: {
    className: "bg-destructive text-destructive-foreground border-transparent",
    label: "Error",
  },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || {
    className: "bg-muted text-muted-foreground border-transparent",
    label: status,
  };
  return (
    <Badge className={cn("text-xs font-medium", config.className)}>
      {config.label}
    </Badge>
  );
}
