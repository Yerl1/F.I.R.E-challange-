"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import {
  Shield,
  Ticket,
  Building2,
  Users,
  Activity,
  LogOut,
  ChevronLeft,
  Menu,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navItems = [
  { href: "/specialist/tickets", label: "Tickets", icon: Ticket },
  { href: "/admin/offices", label: "Offices", icon: Building2 },
  { href: "/admin/specialists", label: "Specialists", icon: Users },
  { href: "/health", label: "Health", icon: Activity },
  { href: "/backend-tools", label: "Backend Tools", icon: Wrench },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { profile, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed left-4 top-3 z-50 flex size-10 items-center justify-center rounded-lg border border-sidebar-border bg-sidebar text-sidebar-foreground lg:hidden"
        aria-label="Toggle menu"
      >
        <Menu className="size-5" />
      </button>

      {/* Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-all duration-200",
          collapsed ? "w-[68px]" : "w-64",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center gap-2.5 border-b border-sidebar-border px-4">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary">
            <Shield className="size-4 text-sidebar-primary-foreground" />
          </div>
          {!collapsed && (
            <span className="text-sm font-semibold tracking-tight">
              Freedom Broker
            </span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="ml-auto hidden rounded-md p-1 text-sidebar-foreground/50 hover:text-sidebar-foreground lg:block"
            aria-label="Collapse sidebar"
          >
            <ChevronLeft
              className={cn("size-4 transition-transform", collapsed && "rotate-180")}
            />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-1 p-3">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                )}
              >
                <item.icon className="size-4.5 shrink-0" />
                {!collapsed && item.label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border p-3">
          {profile && !collapsed && (
            <div className="mb-3 rounded-lg bg-sidebar-accent/50 px-3 py-2.5">
              <p className="text-sm font-medium">{profile.full_name}</p>
              <p className="text-xs text-sidebar-foreground/60">{profile.role}</p>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className={cn(
              "w-full justify-start text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground",
              collapsed && "justify-center px-0"
            )}
          >
            <LogOut className="size-4" />
            {!collapsed && <span className="ml-2">Sign Out</span>}
          </Button>
        </div>
      </aside>
    </>
  );
}
