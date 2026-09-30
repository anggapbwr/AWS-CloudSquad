"use client";

import React from "react";
import {
  Play,
  Plus,
  RefreshCw,
  FileText,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Wifi,
  Cpu,
  DollarSign,
  ChevronRight,
} from "lucide-react";

interface HeaderProps {
  missionName: string;
  missionStatus: string;
  region: string;
  currentStage?: string | null;
  estimatedCost?: number;
  isRunning: boolean;
  onLaunch: () => void;
  onCreateNew: () => void;
  onViewReport: () => void;
  canViewReport: boolean;
}

const StatusPill = ({ status }: { status: string }) => {
  if (status === "COMPLETED")
    return (
      <span className="badge badge-emerald">
        <CheckCircle2 size={9} />
        Completed
      </span>
    );
  if (status === "FAILED")
    return (
      <span className="badge badge-rose">
        <AlertTriangle size={9} />
        Failed
      </span>
    );
  if (status === "CREATED")
    return (
      <span className="badge badge-indigo">Ready</span>
    );
  return (
    <span className="badge badge-cyan animate-pulse">
      <RefreshCw size={9} className="animate-spin" />
      {status.replace(/_/g, " ")}
    </span>
  );
};

const MetaBit = ({
  label,
  value,
  valueClass = "text-[#f0f4ff]",
  icon: Icon,
}: {
  label: string;
  value: string;
  valueClass?: string;
  icon: React.ElementType;
}) => (
  <div className="flex flex-col gap-0.5 min-w-0">
    <span className="text-[9px] font-semibold uppercase tracking-widest text-[#4a5568] font-mono flex items-center gap-1">
      <Icon size={8} />
      {label}
    </span>
    <span className={`text-[12px] font-semibold font-mono truncate ${valueClass}`}>
      {value}
    </span>
  </div>
);

export const Header: React.FC<HeaderProps> = ({
  missionName,
  missionStatus,
  region,
  currentStage,
  estimatedCost = 207.0,
  isRunning,
  onLaunch,
  onCreateNew,
  onViewReport,
  canViewReport,
}) => {
  const progressPercent = (() => {
    const stages = ["architect", "database", "application", "infrastructure", "devsecops", "sre"];
    if (!currentStage) return 0;
    const idx = stages.indexOf(currentStage);
    return idx >= 0 ? Math.round(((idx + 1) / stages.length) * 100) : 0;
  })();

  return (
    <header className="header-backdrop sticky top-0 z-50 px-6 py-3.5">
      {/* Progress bar at very top */}
      {isRunning && (
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-[rgba(100,116,139,0.1)]">
          <div
            className="h-full bg-gradient-to-r from-[#00d4ff] via-[#818cf8] to-[#c084fc] transition-all duration-1000"
            style={{ width: `${progressPercent || 15}%` }}
          />
        </div>
      )}

      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4 flex-wrap">
        {/* LEFT: Brand */}
        <div className="flex items-center gap-3.5 min-w-0">
          {/* Logo mark */}
          <div className="relative flex-shrink-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00d4ff] via-[#818cf8] to-[#c084fc] p-px">
              <div className="w-full h-full bg-[#060c1a] rounded-[10px] flex items-center justify-center">
                <ShieldCheck size={16} className="text-[#00d4ff]" />
              </div>
            </div>
            <div
              className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#34d399] border-2 border-[#03060f]"
              style={{ boxShadow: "0 0 8px rgba(52, 211, 153, 0.6)" }}
            />
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] font-bold tracking-[0.15em] uppercase gradient-text-cyan">
                AWS CloudSquad
              </span>
              <ChevronRight size={10} className="text-[#4a5568]" />
              <span className="text-[10px] text-[#4a5568] font-mono">Autonomous DevOps</span>
            </div>
            <div className="flex items-center gap-2.5 min-w-0">
              <h1 className="text-sm font-bold text-white truncate">{missionName}</h1>
              <StatusPill status={missionStatus} />
            </div>
          </div>
        </div>

        {/* CENTER: Live Meta */}
        <div className="hidden lg:flex items-center gap-5 px-5 py-2.5 rounded-xl bg-[rgba(6,12,26,0.8)] border border-[rgba(148,163,184,0.08)] shadow-inner">
          <MetaBit label="Region" value={region} valueClass="text-[#818cf8]" icon={Wifi} />
          <div className="w-px h-8 bg-[rgba(148,163,184,0.06)]" />
          <MetaBit
            label="Active Stage"
            value={currentStage?.toUpperCase() || "STANDBY"}
            valueClass="text-[#00d4ff]"
            icon={Cpu}
          />
          <div className="w-px h-8 bg-[rgba(148,163,184,0.06)]" />
          <MetaBit
            label="Est. Monthly"
            value={`$${estimatedCost.toFixed(2)}`}
            valueClass="text-[#34d399]"
            icon={DollarSign}
          />
        </div>

        {/* RIGHT: Actions */}
        <div className="flex items-center gap-2">
          <button id="btn-create-mission" onClick={onCreateNew} className="btn btn-ghost text-xs">
            <Plus size={13} className="text-[#00d4ff]" />
            New Mission
          </button>

          {canViewReport && (
            <button id="btn-view-report" onClick={onViewReport} className="btn btn-indigo text-xs">
              <FileText size={13} />
              Final Report
            </button>
          )}

          <button
            id="btn-launch-mission"
            onClick={onLaunch}
            disabled={isRunning}
            className="btn btn-primary text-xs"
          >
            {isRunning ? (
              <>
                <RefreshCw size={13} className="animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play size={13} className="fill-white" />
                Launch Mission
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
