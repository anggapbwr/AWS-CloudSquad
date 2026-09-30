"use client";

import React, { useRef, useEffect } from "react";
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  Info,
  Terminal,
  Radio,
} from "lucide-react";
import { MissionEvent } from "@/lib/api";

interface EventTimelineProps {
  events: MissionEvent[];
}

const STAGE_COLORS: Record<string, string> = {
  architect: "#00d4ff",
  database: "#818cf8",
  application: "#60a5fa",
  infrastructure: "#fbbf24",
  devsecops: "#34d399",
  sre: "#c084fc",
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "passed":
    case "COMPLETED":
      return <CheckCircle2 size={12} className="text-[#34d399] shrink-0 mt-0.5" />;
    case "failed":
    case "FAILED":
    case "warning":
      return <AlertTriangle size={12} className="text-[#fb7185] shrink-0 mt-0.5" />;
    case "running":
      return <Clock size={12} className="text-[#00d4ff] animate-spin shrink-0 mt-0.5" />;
    default:
      return <Info size={12} className="text-[#4a5568] shrink-0 mt-0.5" />;
  }
};

const formatTime = (ts: string) => {
  try {
    return new Date(ts).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return ts;
  }
};

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  return (
    <div
      className="panel flex flex-col h-[520px]"
      style={{ boxShadow: "0 0 0 1px rgba(0,212,255,0.08), 0 4px 40px rgba(0,0,0,0.4)" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-4 pb-3" style={{ borderBottom: "1px solid rgba(148,163,184,0.06)" }}>
        <div className="flex items-center gap-2.5">
          <Terminal size={14} className="text-[#00d4ff]" />
          <div>
            <h2 className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#f0f4ff]">
              Audit Stream
            </h2>
            <p className="text-[10px] font-mono text-[#4a5568]">
              {events.length} events captured
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#00d4ff]">
          <Radio size={10} className="animate-pulse" />
          <span>Live</span>
        </div>
      </div>

      {/* Events */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1.5">
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ background: "rgba(0,212,255,0.06)", border: "1px solid rgba(0,212,255,0.12)" }}
            >
              <Terminal size={16} className="text-[#4a5568]" />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-[#4a5568]">Awaiting pipeline trigger</p>
              <p className="text-[10px] font-mono text-[#2d3748] mt-0.5">
                Launch a mission to see live events
              </p>
            </div>
          </div>
        ) : (
          events.map((evt, idx) => {
            const stageColor = evt.stage ? STAGE_COLORS[evt.stage] : undefined;
            return (
              <div
                key={evt.id || idx}
                className="event-item flex items-start gap-2.5 animate-slide-up"
                style={{ animationDelay: `${Math.min(idx * 20, 200)}ms` }}
              >
                {getStatusIcon(evt.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[10px] font-mono text-[#4a5568]">
                      {formatTime(evt.timestamp)}
                    </span>
                    {evt.stage && (
                      <span
                        className="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full font-mono"
                        style={{
                          background: stageColor ? `${stageColor}15` : "rgba(100,116,139,0.1)",
                          color: stageColor || "#64748b",
                          border: `1px solid ${stageColor ? stageColor + "30" : "rgba(100,116,139,0.15)"}`,
                        }}
                      >
                        {evt.stage}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-[#8892aa] leading-snug break-words">
                    {evt.message}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
