"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Send, Bot, User, Sparkles } from "lucide-react";
import { isMockMode } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ChatMessage, AssistantResponse } from "@/lib/types";

const SUGGESTED_REPLIES = [
  "Could you please provide more details?",
  "I have reviewed your request and we are processing it.",
  "Let me check this with a senior specialist.",
];

export function ChatPanel({ ticketId }: { ticketId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function handleSend(text?: string) {
    const msg = (text || input).trim();
    if (!msg) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "specialist", content: msg }]);
    setIsLoading(true);

    try {
      let res: AssistantResponse;
      await new Promise((r) => setTimeout(r, isMockMode() ? 1000 : 350));
      res = {
        answer:
          "Assistant endpoint is not exposed in current backend. Use recommendation/summary from ticket card for now.",
        thread_id: threadId || `local-thread-${ticketId}`,
      };
      setThreadId(res.thread_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer }]);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Assistant error");
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <Bot className="size-4 text-primary" />
          AI Assistant
        </CardTitle>
        {threadId && (
          <p className="text-xs text-muted-foreground font-mono">
            Thread: {threadId}
          </p>
        )}
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-3 pb-4">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto pr-2 max-h-[400px]" ref={scrollRef}>
          <div className="space-y-4 min-h-[200px]">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Sparkles className="mb-3 size-8 text-muted-foreground/40" />
                <p className="text-sm text-muted-foreground">
                  Ask the AI assistant for help with this ticket
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex gap-3",
                  msg.role === "specialist" && "justify-end"
                )}
              >
                {msg.role !== "specialist" && (
                  <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="size-3.5 text-primary" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[85%] rounded-lg px-3.5 py-2.5 text-sm leading-relaxed",
                    msg.role === "specialist"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  )}
                >
                  {msg.content}
                </div>
                {msg.role === "specialist" && (
                  <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                    <User className="size-3.5 text-muted-foreground" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3">
                <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <Bot className="size-3.5 text-primary" />
                </div>
                <div className="rounded-lg bg-muted px-3.5 py-2.5">
                  <Loader2 className="size-4 animate-spin text-muted-foreground" />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Suggested replies */}
        {messages.length === 0 && (
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_REPLIES.map((r) => (
              <button
                key={r}
                onClick={() => handleSend(r)}
                className="rounded-full border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                {r}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="flex gap-2">
          <Input
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            size="icon"
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
          >
            <Send className="size-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
