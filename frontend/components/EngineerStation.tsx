"use client";

import React from "react";
import {
  Compass,
  Database,
  Cpu,
  Boxes,
  ShieldCheck,
  Activity,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileCode2,
  RefreshCw,
  Layers,
} from "lucide-react";

export interface AgentCardData {
  id: string;
  name: string;
  role: string;
  status: "WAITING" | "RUNNING" | "COMPLETED" | "FAILED" | "BLOCKED";
  durationSeconds?: number;
  summary?: string;
  artifactsCount?: number;
  lastEventMessage?: string;
}

interface EngineerStationProps {
  agents: AgentCardData[];
  onInspectArtifacts: (agentId: string) => void;
}

const AGENT_META: Record<
  string,
  { icon: React.ElementType; color: string; bg: string; gradFrom: string; gradTo: string }
> = {
  architect:      { icon: Compass,     color: "#00d4ff", bg: "rgba(0,212,255,0.08)",    gradFrom: "#00d4ff", gradTo: "#818cf8" },
  database:       { icon: Database,    color: "#818cf8", bg: "rgba(129,140,248,0.08)",   gradFrom: "#818cf8", gradTo: "#60a5fa" },
  application:    { icon: Cpu,         color: "#60a5fa", bg: "rgba(96,165,250,0.08)",    gradFrom: "#60a5fa", gradTo: "#a78bfa" },
  infrastructure: { icon: Boxes,       color: "#fbbf24", bg: "rgba(251,191,36,0.08)",    gradFrom: "#fbbf24", gradTo: "#f97316" },
  devsecops:      { icon: ShieldCheck, color: "#34d399", bg: "rgba(52,211,153,0.08)",    gradFrom: "#34d399", gradTo: "#06b6d4" },
  sre:            { icon: Activity,    color: "#c084fc", bg: "rgba(192,132,252,0.08)",   gradFrom: "#c084fc", gradTo: "#f472b6" },
};

const getStatusConfig = (status: AgentCardData["status"]) => {
  switch (status) {
    case "COMPLETED":
      return { label: "Completed", cls: "badge-emerald", icon: CheckCircle2 };
    case "RUNNING":
      return { label: "Running", cls: "badge-cyan", icon: RefreshCw, spin: true, pulse: true };
    case "FAILED":
    case "BLOCKED":
      return { label: status, cls: "badge-rose", icon: AlertTriangle };
    default:
      return { label: "Waiting", cls: "badge-slate", icon: Clock };
  }
};

const AgentCard: React.FC<{
  agent: AgentCardData;
  onInspectArtifacts: (id: string) => void;
}> = ({ agent, onInspectArtifacts }) => {
  const meta = AGENT_META[agent.id] || {
    icon: Layers,
    color: "#94a3b8",
    bg: "rgba(100,116,139,0.08)",
    gradFrom: "#94a3b8",
    gradTo: "#64748b",
  };
  const Icon = meta.icon;
  const statusCfg = getStatusConfig(agent.status);
  const StatusIcon = statusCfg.icon;

  const isRunning = agent.status === "RUNNING";
  const isCompleted = agent.status === "COMPLETED";
  const isFailed = agent.status === "FAILED" || agent.status === "BLOCKED";

  return (
    <div
      className={`agent-card flex flex-col ${
        isRunning ? "running" : isCompleted ? "completed" : isFailed ? "failed" : ""
      }`}
      style={{ padding: "16px" }}
    >
      {/* Top accent line */}
      {(isRunning || isCompleted) && (
        <div
          className="absolute top-0 left-4 right-4 h-[1px] rounded-full"
          style={{
            background: `linear-gradient(90deg, transparent, ${meta.color}40, transparent)`,
          }}
        />
      )}

      {/* Agent Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 relative"
          style={{
            background: meta.bg,
            border: `1px solid ${meta.color}25`,
            boxShadow: isRunning ? `0 0 16px ${meta.color}20` : "none",
          }}
        >
          <Icon size={16} style={{ color: meta.color }} />
          {isRunning && (
            <div
              className="absolute inset-0 rounded-xl animate-ping opacity-20"
              style={{ background: meta.color }}
            />
          )}
        </div>

        <span className={`badge ${statusCfg.cls} ${statusCfg.pulse ? "animate-pulse" : ""}`}>
          <StatusIcon size={9} className={statusCfg.spin ? "animate-spin" : ""} />
          {statusCfg.label}
        </span>
      </div>

      {/* Name & Role */}
      <div className="mb-2">
        <h3
          className="text-[12px] font-bold tracking-wide mb-0.5"
          style={{ color: isCompleted ? meta.color : isRunning ? "#f0f4ff" : "#8892aa" }}
        >
          {agent.name}
        </h3>
        <p className="text-[10px] font-mono" style={{ color: "#4a5568" }}>
          {agent.role}
        </p>
      </div>

      {/* Summary */}
      <p
        className="text-[11px] leading-relaxed line-clamp-3 flex-1 min-h-[48px]"
        style={{ color: isRunning ? "#a0aec0" : "#4a5568" }}
      >
        {agent.summary ||
          (isRunning
            ? "Executing analysis pipeline and generating production artifacts..."
            : "Awaiting upstream stage completion...")}
      </p>

      {/* Footer */}
      <div
        className="mt-3 pt-2.5 flex items-center justify-between"
        style={{ borderTop: "1px solid rgba(148,163,184,0.06)" }}
      >
        <span className="text-[10px] font-mono" style={{ color: "#4a5568" }}>
          {agent.durationSeconds ? (
            <span style={{ color: "#8892aa" }}>{agent.durationSeconds}s</span>
          ) : (
            "—"
          )}
        </span>

        {agent.artifactsCount ? (
          <button
            onClick={() => onInspectArtifacts(agent.id)}
            className="flex items-center gap-1.5 text-[10px] font-semibold font-mono transition-all hover:opacity-80 cursor-pointer"
            style={{ color: meta.color }}
          >
            <FileCode2 size={11} />
            {agent.artifactsCount} files
          </button>
        ) : (
          <span className="text-[10px] font-mono" style={{ color: "#4a5568" }}>
            0 artifacts
          </span>
        )}
      </div>
    </div>
  );
};

export const EngineerStation: React.FC<EngineerStationProps> = ({
  agents,
  onInspectArtifacts,
}) => {
  const completedCount = agents.filter((a) => a.status === "COMPLETED").length;
  const runningCount = agents.filter((a) => a.status === "RUNNING").length;

  return (
    <div className="panel panel-glow-cyan">
      {/* Header */}
      <div className="flex items-center justify-between mb-5 px-5 pt-5">
        <div className="flex items-center gap-3">
          <div className="live-dot text-[#00d4ff]" style={{ color: "#00d4ff" }}>
            <div
              className="w-2 h-2 rounded-full"
              style={{
                background: "#00d4ff",
                boxShadow: "0 0 8px rgba(0,212,255,0.6)",
                animation: runningCount > 0 ? "pulse 1s ease-in-out infinite" : "none",
              }}
            />
          </div>
          <div>
            <h2 className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#f0f4ff]">
              Engineering Squad
            </h2>
            <p className="text-[10px] font-mono text-[#4a5568]">
              Autonomous Execution Matrix · 6 AI Agents
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Progress */}
          <div className="hidden sm:flex items-center gap-2">
            <div className="w-32 progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${(completedCount / agents.length) * 100}%` }}
              />
            </div>
            <span className="text-[10px] font-mono text-[#8892aa]">
              {completedCount}/{agents.length}
            </span>
          </div>

          {runningCount > 0 && (
            <span className="badge badge-cyan animate-pulse">
              <RefreshCw size={9} className="animate-spin" />
              {runningCount} Active
            </span>
          )}
        </div>
      </div>

      {/* Grid */}
      <div className="px-5 pb-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onInspectArtifacts={onInspectArtifacts}
          />
        ))}
      </div>
    </div>
  );
};
