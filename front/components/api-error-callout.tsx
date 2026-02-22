import { AlertCircle } from "lucide-react";

export function ApiErrorCallout({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
      <AlertCircle className="mt-0.5 size-5 shrink-0 text-destructive" />
      <div>
        <p className="text-sm font-medium text-destructive">Something went wrong</p>
        <p className="mt-1 text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}
