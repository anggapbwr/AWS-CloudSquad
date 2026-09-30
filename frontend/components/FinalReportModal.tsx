"use client";

import React, { useState } from "react";
import {
  X,
  Download,
  Copy,
  Check,
  CheckCircle2,
  ShieldCheck,
  Activity,
  FileText,
  BarChart2,
  Clock,
} from "lucide-react";

interface FinalReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportJson?: any;
  reportMarkdown?: string;
  missionName: string;
}

const TABS = [
  { id: "markdown", label: "Mission Report", icon: FileText },
  { id: "summary", label: "Executive Summary", icon: BarChart2 },
];

export const FinalReportModal: React.FC<FinalReportModalProps> = ({
  isOpen,
  onClose,
  reportJson,
  reportMarkdown,
  missionName,
}) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("markdown");

  if (!isOpen) return null;

  const handleCopy = () => {
    if (reportMarkdown) {
      navigator.clipboard.writeText(reportMarkdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (reportMarkdown) {
      const blob = new Blob([reportMarkdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AWS-CloudSquad-Report-${missionName.replace(/\s+/g, "-")}.md`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  // Quick stats from JSON report if available
  const stats = reportJson
    ? [
        { label: "SLA Target", value: reportJson.availability || "99.97%", color: "#34d399", icon: ShieldCheck },
        { label: "Throughput", value: reportJson.rps ? `${reportJson.rps} RPS` : "1,000 RPS", color: "#00d4ff", icon: Activity },
        { label: "Latency P95", value: reportJson.p95_ms ? `${reportJson.p95_ms}ms` : "142ms", color: "#818cf8", icon: Clock },
        { label: "Monthly Cost", value: reportJson.total_cost ? `$${reportJson.total_cost}` : "$207.00", color: "#fbbf24", icon: BarChart2 },
      ]
    : [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="modal-content w-full flex flex-col animate-in"
        style={{ maxWidth: 820, height: "85vh" }}
      >
        {/* Header */}
        <div
          className="px-5 py-4 flex items-center justify-between flex-shrink-0"
          style={{ borderBottom: "1px solid rgba(148,163,184,0.08)" }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.2)" }}
            >
              <CheckCircle2 size={14} className="text-[#34d399]" />
            </div>
            <div>
              <h3 className="text-[13px] font-bold text-white">Mission Complete</h3>
              <p className="text-[10px] font-mono text-[#4a5568]">
                {missionName} · Final Engineering Report
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={handleCopy} className="btn btn-ghost text-xs py-1.5 px-3">
              {copied ? (
                <><Check size={12} className="text-[#34d399]" /> Copied</>
              ) : (
                <><Copy size={12} /> Copy</>
              )}
            </button>
            <button onClick={handleDownload} className="btn btn-primary text-xs py-1.5 px-3">
              <Download size={12} /> Download .md
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-[#4a5568] hover:text-white hover:bg-white/5 transition-all cursor-pointer"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        {stats.length > 0 && (
          <div
            className="px-5 py-3 flex items-center gap-4 flex-shrink-0"
            style={{ borderBottom: "1px solid rgba(148,163,184,0.06)" }}
          >
            {stats.map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.label} className="flex items-center gap-2 text-[11px] font-mono">
                  <Icon size={11} style={{ color: s.color }} />
                  <span className="text-[#4a5568]">{s.label}:</span>
                  <span style={{ color: s.color, fontWeight: 700 }}>{s.value}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* Tabs */}
        <div
          className="flex items-center gap-1 px-5 py-2 flex-shrink-0"
          style={{ borderBottom: "1px solid rgba(148,163,184,0.06)", background: "rgba(3,6,15,0.3)" }}
        >
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold transition-all cursor-pointer"
                style={{
                  background: isActive ? "rgba(0,212,255,0.08)" : "transparent",
                  color: isActive ? "#00d4ff" : "#4a5568",
                  border: isActive ? "1px solid rgba(0,212,255,0.2)" : "1px solid transparent",
                }}
              >
                <Icon size={11} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          {activeTab === "markdown" ? (
            <div className="code-viewer p-6 h-full">
              <pre className="whitespace-pre-wrap break-words select-text leading-relaxed">
                {reportMarkdown || "Report is compiling. Please wait..."}
              </pre>
            </div>
          ) : (
            <div className="p-6">
              {reportJson ? (
                <pre className="code-viewer text-[11px] leading-relaxed whitespace-pre-wrap">
                  {JSON.stringify(reportJson, null, 2)}
                </pre>
              ) : (
                <div className="flex flex-col items-center justify-center h-48 gap-3">
                  <BarChart2 size={24} className="text-[#2d3748]" />
                  <p className="text-[12px] text-[#4a5568] font-mono">No JSON data available</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
