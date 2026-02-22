import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  MapPin,
  ShieldAlert,
  Users,
  ArrowRight,
  Building2,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: MapPin,
    title: "Auto Office Selection",
    description:
      "Automatically detects your city from the request text and routes you to the nearest available branch office.",
  },
  {
    icon: ShieldAlert,
    title: "VIP & Complaint Rules",
    description:
      "Hard business rules ensure VIP clients and complaints are escalated to senior specialists immediately.",
  },
  {
    icon: Users,
    title: "Fair Round-Robin Assignment",
    description:
      "Workload is distributed evenly across specialists using intelligent round-robin allocation.",
  },
];

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.03] to-transparent" />
        <div className="relative mx-auto max-w-5xl px-4 py-24 sm:px-6 sm:py-32 lg:py-40">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-sm text-muted-foreground">
              <Building2 className="size-4" />
              Intelligent Request Routing
            </div>
            <h1 className="text-balance text-4xl font-semibold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Freedom Broker
            </h1>
            <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground sm:text-xl">
              Smart routing of customer requests. We automatically match you
              with the right office and specialist.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button size="lg" asChild className="w-full sm:w-auto">
                <Link href="/create-ticket">
                  Create a Ticket
                  <ArrowRight className="ml-2 size-4" />
                </Link>
              </Button>

            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-4 py-20 sm:px-6">
        <div className="mb-12 text-center">
          <div className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-primary">
            <BarChart3 className="size-4" />
            How It Works
          </div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
            Automated, fair, and transparent
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
            Our system analyzes your request, determines the best branch, and
            assigns a qualified specialist — all in seconds.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map((f) => (
            <Card
              key={f.title}
              className="group transition-shadow hover:shadow-md"
            >
              <CardContent className="pt-6">
                <div className="mb-4 flex size-10 items-center justify-center rounded-lg bg-primary/10">
                  <f.icon className="size-5 text-primary" />
                </div>
                <h3 className="mb-2 font-semibold text-foreground">
                  {f.title}
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {f.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-8 sm:px-6">
          <p className="text-sm text-muted-foreground">
            Freedom Broker &middot; Secure request routing platform
          </p>
          <div className="flex gap-4 text-sm text-muted-foreground">
            <Link
              href="/create-ticket"
              className="transition-colors hover:text-foreground"
            >
              Create Ticket
            </Link>
            <Link
              href="/ticket-status"
              className="transition-colors hover:text-foreground"
            >
              Status
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
