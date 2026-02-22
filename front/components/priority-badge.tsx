import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const priorityConfig: Record<string, { className: string; label: string }> = {
  URGENT: {
    className: "bg-destructive/10 text-destructive border-destructive/20",
    label: "Urgent",
  },
  HIGH: {
    className: "bg-warning/10 text-warning-foreground border-warning/20",
    label: "High",
  },
  MEDIUM: {
    className: "bg-primary/10 text-primary border-primary/20",
    label: "Medium",
  },
  LOW: {
    className: "bg-muted text-muted-foreground border-border",
    label: "Low",
  },
};

export function PriorityBadge({ priority }: { priority: string }) {
  const config = priorityConfig[priority] || {
    className: "bg-muted text-muted-foreground border-border",
    label: priority,
  };
  return (
    <Badge variant="outline" className={cn("text-xs font-medium", config.className)}>
      {config.label}
    </Badge>
  );
}
