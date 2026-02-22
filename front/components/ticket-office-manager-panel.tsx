import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, UserCheck, MapPin } from "lucide-react";
import type { Office, Manager } from "@/lib/types";

export function TicketOfficeManagerPanel({
  ticketId,
  office,
  manager,
}: {
  ticketId: string;
  office?: Office;
  manager?: Manager;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 rounded-lg border border-success/30 bg-success/5 px-4 py-3">
        <div className="size-2 rounded-full bg-success" />
        <p className="text-sm font-medium text-foreground">
          Ticket <span className="font-mono">{ticketId}</span> has been successfully processed
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {office && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <Building2 className="size-4" />
                Assigned Office
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="font-semibold text-foreground">{office.name}</p>
              <div className="flex items-start gap-1.5 text-sm text-muted-foreground">
                <MapPin className="mt-0.5 size-3.5 shrink-0" />
                <span>{office.address}, {office.city}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {manager && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <UserCheck className="size-4" />
                Assigned Manager
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="font-semibold text-foreground">{manager.full_name}</p>
              <p className="text-sm text-muted-foreground">{manager.role}</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
