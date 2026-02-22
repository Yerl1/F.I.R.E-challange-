"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, Send, ArrowRight, Paperclip, X, FileText, ImageIcon, File } from "lucide-react";
import { apiFetch, isMockMode } from "@/lib/api";
import { MOCK_CREATE_RESPONSE } from "@/lib/mock-data";
import { TicketOfficeManagerPanel } from "@/components/ticket-office-manager-panel";
import type { CreateTicketResponse } from "@/lib/types";

export default function CreateTicketPage() {
  const [rawText, setRawText] = useState("");
  const [segment, setSegment] = useState("Mass");

  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<CreateTicketResponse | null>(null);
  const MAX_FILES = 5;
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = Array.from(e.target.files || []);
    const valid: File[] = [];
    for (const file of selected) {
      if (file.size > MAX_FILE_SIZE) {
        toast.error(`"${file.name}" exceeds the 10 MB limit.`);
        continue;
      }
      valid.push(file);
    }
    setFiles((prev) => {
      const combined = [...prev, ...valid];
      if (combined.length > MAX_FILES) {
        toast.error(`You can attach up to ${MAX_FILES} files.`);
        return combined.slice(0, MAX_FILES);
      }
      return combined;
    });
    // reset so re-selecting the same file works
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  function getFileIcon(file: File) {
    if (file.type.startsWith("image/")) return <ImageIcon className="size-4 shrink-0 text-muted-foreground" />;
    if (file.type === "application/pdf") return <FileText className="size-4 shrink-0 text-muted-foreground" />;
    return <File className="size-4 shrink-0 text-muted-foreground" />;
  }

  function formatFileSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!rawText.trim()) {
      toast.error("Please describe your request.");
      return;
    }
    setIsSubmitting(true);
    setResult(null);
    try {
      let res: CreateTicketResponse;
      if (isMockMode()) {
        await new Promise((r) => setTimeout(r, 1200));
        res = { ...MOCK_CREATE_RESPONSE };
      } else {
        const ticketId = "WEB-" + Date.now();
        const payload = {
          ticket_id: ticketId,
          raw_text: rawText.trim(),
          segment,
          country: "",
          region: "",
          city: "",
          street: "",
          house: "",
          attachments: files.map((f) => f.name).join(", "),
        };
        const backend = await apiFetch<Record<string, unknown>>("/api/v1/tickets/process-one", {
          method: "POST",
          body: { payload },
        });
        const ticket = (backend.ticket || {}) as Record<string, unknown>;
        res = {
          ticket_id: String(ticket.ticket_id || ticketId),
          status: "DONE",
          office: ticket.office_name
            ? {
                name: String(ticket.office_name),
                address: String(ticket.office_address || ""),
                city: String(ticket.city || ticket.office_name || ""),
              }
            : undefined,
          manager: ticket.manager_name
            ? {
                full_name: String(ticket.manager_name),
                role: "Assigned manager",
              }
            : undefined,
        };
      }
      setResult(res);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create ticket");
    } finally {
      setIsSubmitting(false);
    }
  }

  const isDone = result && result.status !== "PROCESSING";

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Create a Ticket
        </h1>
        <p className="mt-1 text-muted-foreground">
          Describe your request and we will route it to the right office and specialist.
        </p>
      </div>

      {!result ? (
        <Card>
          <CardHeader>
            <CardTitle>New Request</CardTitle>
            <CardDescription>
              Please provide details about your inquiry
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="raw_text">Describe your request</Label>
                <Textarea
                  id="raw_text"
                  placeholder="e.g., I would like to open a business account in Astana and discuss corporate loan options..."
                  rows={6}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  className="resize-none"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="segment">Client Segment</Label>
                <Select value={segment} onValueChange={setSegment}>
                  <SelectTrigger id="segment">
                    <SelectValue placeholder="Select segment" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="VIP">VIP</SelectItem>
                    <SelectItem value="Priority">Priority</SelectItem>
                    <SelectItem value="Mass">Mass</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* File attachment */}
              <div className="space-y-2">
                <Label>Attachments <span className="text-muted-foreground">(optional)</span></Label>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  className="hidden"
                  onChange={handleFileSelect}
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif,.webp,.txt,.csv"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border bg-muted/30 px-4 py-3 text-sm text-muted-foreground transition-colors hover:border-primary/40 hover:bg-muted/50"
                >
                  <Paperclip className="size-4" />
                  Click to attach files
                  <span className="text-xs">({files.length}/{MAX_FILES})</span>
                </button>

                {files.length > 0 && (
                  <ul className="space-y-1.5">
                    {files.map((file, idx) => (
                      <li
                        key={`${file.name}-${idx}`}
                        className="flex items-center gap-2 rounded-md border border-border bg-muted/40 px-3 py-2 text-sm"
                      >
                        {getFileIcon(file)}
                        <span className="min-w-0 flex-1 truncate text-foreground">{file.name}</span>
                        <span className="shrink-0 text-xs text-muted-foreground">{formatFileSize(file.size)}</span>
                        <button
                          type="button"
                          onClick={() => removeFile(idx)}
                          className="ml-1 shrink-0 rounded-full p-0.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                          aria-label={`Remove ${file.name}`}
                        >
                          <X className="size-3.5" />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <Button type="submit" disabled={isSubmitting} className="w-full">
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 size-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 size-4" />
                    Send
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Ticket Created</CardTitle>
              <CardDescription>Use this ID to check status later.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">Ticket ID</p>
              <p className="font-mono text-lg font-semibold">{result.ticket_id}</p>
              <p className="text-sm text-muted-foreground">Status: {result.status}</p>
            </CardContent>
          </Card>

          {/* Sync response with office + manager */}
          {isDone && result.office && result.manager && (
            <TicketOfficeManagerPanel
              ticketId={result.ticket_id}
              office={result.office}
              manager={result.manager}
            />
          )}

          {/* Actions */}
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button variant="outline" onClick={() => {
              setResult(null);
              setRawText("");
              setSegment("Mass");
              setFiles([]);
            }}>
              Create Another Ticket
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/ticket-status">
                Check Ticket Status
                <ArrowRight className="ml-2 size-4" />
              </Link>
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
