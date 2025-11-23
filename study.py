import React, { useState, useEffect } from "react";
import { Send, Mic, Volume2, Trash2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
  time: string;
}

interface ChatInterfaceProps {
  toolId: string;
  toolName: string;
  description: string;
}

export function ChatInterface({ toolId, toolName, description }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // Reset chat when tool changes
  useEffect(() => {
    setMessages([]);
    setMessages([
      {
        role: "assistant",
        content: `Hello! I'm your ${toolName}. ${description}. How can I help you today?`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [toolId, toolName, description]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      role: "user",
      content: input,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // Simulate AI delay and response
    setTimeout(() => {
      const aiMsg: Message = {
        role: "assistant",
        content: generateMockResponse(toolId, input),
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsg]);
      setIsTyping(false);
    }, 1500);
  };

  // ... (Mock response generator logic omitted for brevity)

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            🔹 {toolName}
          </h2>
          <p className="text-sm opacity-70">{description}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="icon" onClick={() => setMessages([])} title="Clear History">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 pr-4 -mr-4 mb-4">
        <div className="space-y-4 pb-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={cn(
                "p-4 rounded-xl max-w-[85%] animate-in slide-in-from-bottom-2 duration-300",
                msg.role === "user" 
                  ? "ml-auto chat-bubble-user text-right" 
                  : "mr-auto chat-bubble-genie"
              )}
            >
              <div className="font-medium text-xs opacity-50 mb-1">
                {msg.role === "user" ? "You" : "Genie"} • {msg.time}
              </div>
              <div className="whitespace-pre-wrap leading-relaxed">
                {msg.content}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="mr-auto chat-bubble-genie p-4 rounded-xl animate-pulse">
              Thinking...
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="mt-auto card-glass p-4 rounded-xl">
        <div className="flex gap-2">
          <Textarea 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={`Ask ${toolName}...`}
            className="bg-transparent border-none resize-none focus-visible:ring-0 min-h-[60px]"
          />
          <div className="flex flex-col gap-2 justify-end">
            <Button size="icon" variant="ghost" title="Voice Input (Mock)">
              <Mic className="h-4 w-4" />
            </Button>
            <Button size="icon" onClick={handleSend} disabled={!input.trim() || isTyping}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}